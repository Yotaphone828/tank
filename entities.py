"""游戏实体类：坦克、子弹和障碍物。"""

from typing import Dict, Iterable, Tuple
import pygame

from config import (
    DEFAULT_TANK_HEALTH,
    DEFAULT_TANK_RELOAD_MS,
    BULLET_SPEED,
    COLLISION_PUSH_DISTANCE,
    TANK_COLLISION_THRESHOLD,
)
from graphics import orientation_from_vector, get_bullet_spawn_offset


class Bullet(pygame.sprite.Sprite):
    """带有物理和边界检查的投射物实体。"""

    def __init__(
        self,
        images: Dict[str, pygame.Surface],
        position: Tuple[float, float],
        direction: pygame.Vector2,
        speed: float,
        playfield: pygame.Rect,
        owner: "Tank",
    ) -> None:
        super().__init__()
        self.images = images
        self.direction = pygame.Vector2(direction)
        if self.direction.length_squared() == 0:
            self.direction = pygame.Vector2(0, -1)
        else:
            self.direction = self.direction.normalize()
        self.owner = owner
        self.speed = speed
        self.playfield = playfield
        self.orientation = orientation_from_vector(self.direction)
        self.image = self.images[self.orientation]
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(self.rect.center)

    def update(self, dt: float) -> None:
        """更新子弹位置，如果超出边界则移除。"""
        self.position += self.direction * self.speed * dt
        self.rect.center = (round(self.position.x), round(self.position.y))
        if not self.playfield.colliderect(self.rect):
            self.kill()


class Tank(pygame.sprite.Sprite):
    """具有移动、射击、生命值和碰撞检测功能的主要游戏实体。"""

    def __init__(
        self,
        images: Dict[str, pygame.Surface],
        position: Tuple[int, int],
        speed: float,
        playfield: pygame.Rect,
        health: int = DEFAULT_TANK_HEALTH,
        reload_ms: int = DEFAULT_TANK_RELOAD_MS,
    ) -> None:
        super().__init__()
        self.images = images
        self.orientation = "up"
        self.image = self.images[self.orientation]
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(self.rect.center)
        self.speed = speed
        self.playfield = playfield
        self.health = health
        self.reload_ms = reload_ms
        self._last_shot = 0
        self._move_vector = pygame.Vector2(0, 0)

    def move(self, direction: pygame.Vector2, dt: float, blockers: Iterable[pygame.sprite.Sprite] | None = None) -> None:
        """移动坦克，带有碰撞检测和滑动机制。"""
        self._move_vector = pygame.Vector2(direction)
        if self._move_vector.length_squared() > 0:
            self._move_vector = self._move_vector.normalize()
            self.orientation = orientation_from_vector(self._move_vector)
            self.image = self.images[self.orientation]

        # 本帧的预期位移
        dx, dy = (self._move_vector * self.speed * dt)

        # 存储原始位置
        original_pos = pygame.Vector2(self.position)

        # 尝试斜向或水平移动
        if dx != 0 or dy != 0:
            self.position.x += dx
            self.position.y += dy
            self.rect.center = (round(self.position.x), round(self.position.y))

            # 保持在游戏场地内
            if not self.playfield.contains(self.rect):
                self.rect.clamp_ip(self.playfield)
                self.position.x = self.rect.centerx
                self.position.y = self.rect.centery

            # 检查并解决与阻挡者的碰撞
            collision_occurred = False
            if blockers is not None:
                for b in blockers:
                    if b is self:
                        continue
                    if hasattr(b, "rect") and self.rect.colliderect(b.rect):
                        collision_occurred = True
                        # Push tanks apart
                        delta_x = self.rect.centerx - b.rect.centerx
                        delta_y = self.rect.centery - b.rect.centery
                        distance = (delta_x**2 + delta_y**2)**0.5

                        if distance > 0:
                            # Normalize and push away
                            push_x = delta_x / distance * COLLISION_PUSH_DISTANCE
                            push_y = delta_y / distance * COLLISION_PUSH_DISTANCE

                            # Only push if we're overlapping
                            if abs(delta_x) < TANK_COLLISION_THRESHOLD and abs(delta_y) < TANK_COLLISION_THRESHOLD:
                                if abs(delta_x) > abs(delta_y):
                                    self.position.x += push_x
                                else:
                                    self.position.y += push_y

                            self.rect.center = (round(self.position.x), round(self.position.y))

            # If still overlapping after resolution, try sliding movement
            if collision_occurred and blockers is not None:
                for b in blockers:
                    if b is self:
                        continue
                    if hasattr(b, "rect") and self.rect.colliderect(b.rect):
                        # Slide movement: try moving only in the dominant direction
                        if abs(dx) > abs(dy):
                            # Try only horizontal movement
                            self.position = pygame.Vector2(original_pos)
                            self.position.x += dx
                            self.rect.centerx = round(self.position.x)

                            # Check horizontal collision
                            horizontal_collision = False
                            for b2 in blockers:
                                if b2 is self:
                                    continue
                                if hasattr(b2, "rect") and self.rect.colliderect(b2.rect):
                                    horizontal_collision = True
                                    if dx > 0:
                                        self.rect.right = b2.rect.left
                                    else:
                                        self.rect.left = b2.rect.right
                                    self.position.x = self.rect.centerx

                            if not horizontal_collision:
                                break
                        else:
                            # Try only vertical movement
                            self.position = pygame.Vector2(original_pos)
                            self.position.y += dy
                            self.rect.centery = round(self.position.y)

                            # Check vertical collision
                            vertical_collision = False
                            for b2 in blockers:
                                if b2 is self:
                                    continue
                                if hasattr(b2, "rect") and self.rect.colliderect(b2.rect):
                                    vertical_collision = True
                                    if dy > 0:
                                        self.rect.bottom = b2.rect.top
                                    else:
                                        self.rect.top = b2.rect.bottom
                                    self.position.y = self.rect.centery

                            if not vertical_collision:
                                break

    def can_fire(self, now_ms: int) -> bool:
        """检查坦克是否可以射击（已装填）。"""
        return (now_ms - self._last_shot) >= self.reload_ms

    def shoot(
        self,
        bullet_images: Dict[str, pygame.Surface],
        bullets: pygame.sprite.Group,
        now_ms: int,
        bullet_speed: float = BULLET_SPEED,
    ) -> None:
        """沿当前坦克朝向射击子弹。"""
        if not self.can_fire(now_ms):
            return

        # Clear direction map - we'll use orientation directly
        direction_map = {
            "up": pygame.Vector2(0, -1),    # Up = negative Y
            "down": pygame.Vector2(0, 1),   # Down = positive Y
            "left": pygame.Vector2(-1, 0),  # Left = negative X
            "right": pygame.Vector2(1, 0),  # Right = positive X
        }
        direction = direction_map[self.orientation]

        # Get bullet dimensions
        bullet_image = bullet_images[self.orientation]
        bullet_width = bullet_image.get_width()
        bullet_height = bullet_image.get_height()

        # Calculate spawn position based on tank's current position and orientation
        # Spawn bullets from the front of the tank in the direction it's facing
        if self.orientation == "up":
            # Tank facing up: spawn from top center
            spawn_x = self.rect.centerx
            spawn_y = self.rect.top - bullet_height // 2
        elif self.orientation == "down":
            # Tank facing down: spawn from bottom center
            spawn_x = self.rect.centerx
            spawn_y = self.rect.bottom + bullet_height // 2
        elif self.orientation == "left":
            # Tank facing left: spawn from left center
            spawn_x = self.rect.left - bullet_width // 2
            spawn_y = self.rect.centery
        else:  # right
            # Tank facing right: spawn from right center
            spawn_x = self.rect.right + bullet_width // 2
            spawn_y = self.rect.centery

        spawn_position = pygame.Vector2(spawn_x, spawn_y)

        bullet = Bullet(
            bullet_images,
            spawn_position,
            direction,
            bullet_speed,
            self.playfield,
            self,
        )
        bullets.add(bullet)
        self._last_shot = now_ms

    def take_hit(self) -> bool:
        """处理坦克受到伤害。如果被摧毁则返回True。"""
        self.health -= 1
        return self.health <= 0

    @property
    def alive(self) -> bool:
        """检查坦克是否仍然存活。"""
        return self.health > 0


class Obstacle(pygame.sprite.Sprite):
    """阻挡坦克移动和子弹的静态障碍物。"""

    def __init__(
        self,
        image: pygame.Surface,
        position: Tuple[int, int],
    ) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(self.rect.center)