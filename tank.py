"""Simple pixel-art tank battle game using pygame."""

from __future__ import annotations

import random
from typing import Dict, Iterable, Tuple

import pygame

WINDOW_SIZE: Tuple[int, int] = (640, 480)
FPS = 60
PIXEL_SIZE = 4
COLOR_BACKGROUND = (18, 20, 26)

PLAYER_TANK_PATTERN = [
    "...111111....",
    "..111333111..",
    ".11133333111.",
    ".11223332211.",
    ".11223332211.",
    ".11233332211.",
    ".11233332211.",
    ".11223332211.",
    ".11223332211.",
    ".11133333111.",
    "..111333111..",
    "...111111....",
    "...11..11....",
    "...11..11....",
]

ENEMY_TANK_PATTERN = PLAYER_TANK_PATTERN

PLAYER_TANK_PALETTE: Dict[str, Tuple[int, int, int]] = {
    "1": (38, 142, 73),
    "2": (54, 168, 88),
    "3": (92, 196, 118),
}

ENEMY_TANK_PALETTE: Dict[str, Tuple[int, int, int]] = {
    "1": (150, 62, 64),
    "2": (184, 90, 70),
    "3": (214, 132, 92),
}

BULLET_PATTERN = [
    "..1..",
    ".111.",
    "11111",
    ".111.",
    "..1..",
]

BULLET_PALETTE: Dict[str, Tuple[int, int, int]] = {
    "1": (240, 222, 120),
}


def create_pixel_surface(pattern: Iterable[str], palette: Dict[str, Tuple[int, int, int]], pixel_size: int) -> pygame.Surface:
    """Create a pygame Surface from a pixel pattern and palette."""
    rows = list(pattern)
    height = len(rows)
    width = len(rows[0]) if rows else 0
    surface = pygame.Surface((width * pixel_size, height * pixel_size), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            color = palette.get(key)
            if color:
                rect = pygame.Rect(x * pixel_size, y * pixel_size, pixel_size, pixel_size)
                surface.fill(color, rect)
    return surface


def create_tank_images(pattern: Iterable[str], palette: Dict[str, Tuple[int, int, int]], pixel_size: int) -> Dict[str, pygame.Surface]:
    base = create_pixel_surface(pattern, palette, pixel_size)
    return {
        "up": base,
        "right": pygame.transform.rotate(base, -90),
        "down": pygame.transform.rotate(base, 180),
        "left": pygame.transform.rotate(base, 90),
    }


def create_bullet_images(pattern: Iterable[str], palette: Dict[str, Tuple[int, int, int]], pixel_size: int) -> Dict[str, pygame.Surface]:
    base = create_pixel_surface(pattern, palette, pixel_size)
    return {
        "up": base,
        "right": pygame.transform.rotate(base, -90),
        "down": pygame.transform.rotate(base, 180),
        "left": pygame.transform.rotate(base, 90),
    }


def orientation_from_vector(direction: pygame.Vector2) -> str:
    """Return the closest cardinal orientation string."""
    if direction.length_squared() == 0:
        return "up"
    if abs(direction.x) > abs(direction.y):
        return "right" if direction.x > 0 else "left"
    return "down" if direction.y > 0 else "up"


class Bullet(pygame.sprite.Sprite):
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
        self.position += self.direction * self.speed * dt
        self.rect.center = (round(self.position.x), round(self.position.y))
        if not self.playfield.colliderect(self.rect):
            self.kill()


class Tank(pygame.sprite.Sprite):
    def __init__(
        self,
        images: Dict[str, pygame.Surface],
        position: Tuple[int, int],
        speed: float,
        playfield: pygame.Rect,
        health: int = 4,
        reload_ms: int = 450,
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

    def move(self, direction: pygame.Vector2, dt: float) -> None:
        self._move_vector = pygame.Vector2(direction)
        if self._move_vector.length_squared() > 0:
            self._move_vector = self._move_vector.normalize()
            self.orientation = orientation_from_vector(self._move_vector)
            self.image = self.images[self.orientation]
        displacement = self._move_vector * self.speed * dt
        self.position += displacement
        self.rect.center = (round(self.position.x), round(self.position.y))
        if not self.playfield.contains(self.rect):
            self.rect.clamp_ip(self.playfield)
            self.position = pygame.Vector2(self.rect.center)

    def can_fire(self, now_ms: int) -> bool:
        return (now_ms - self._last_shot) >= self.reload_ms

    def shoot(
        self,
        bullet_images: Dict[str, pygame.Surface],
        bullets: pygame.sprite.Group,
        now_ms: int,
        bullet_speed: float = 360.0,
    ) -> None:
        if not self.can_fire(now_ms):
            return
        direction_map = {
            "up": pygame.Vector2(0, -1),
            "down": pygame.Vector2(0, 1),
            "left": pygame.Vector2(-1, 0),
            "right": pygame.Vector2(1, 0),
        }
        direction = direction_map[self.orientation]
        if self.orientation in {"up", "down"}:
            muzzle_distance = self.image.get_height() // 2
            bullet_half = bullet_images[self.orientation].get_height() // 2
        else:
            muzzle_distance = self.image.get_width() // 2
            bullet_half = bullet_images[self.orientation].get_width() // 2
        offset = direction * (muzzle_distance + bullet_half)
        spawn_position = self.position + offset
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
        self.health -= 1
        return self.health <= 0

    @property
    def alive(self) -> bool:
        return self.health > 0


def bullet_hits(target: Tank, projectiles: pygame.sprite.Group) -> bool:
    """Check if any projectile has struck the given tank."""
    collisions = pygame.sprite.spritecollide(target, projectiles, dokill=True)
    return bool(collisions)


class EnemyController:
    """Lightweight AI that drives the enemy tank."""

    def __init__(self, tank: Tank) -> None:
        self.tank = tank
        self._direction = pygame.Vector2(0, -1)
        self._decision_timer = 0.0

    def _pick_direction(self, target_pos: pygame.Vector2) -> pygame.Vector2:
        if random.random() < 0.6:
            delta = target_pos - pygame.Vector2(self.tank.rect.center)
            if abs(delta.x) > abs(delta.y):
                return pygame.Vector2(1 if delta.x > 0 else -1, 0)
            if delta.y != 0:
                return pygame.Vector2(0, 1 if delta.y > 0 else -1)
        choices = [
            pygame.Vector2(1, 0),
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, 1),
            pygame.Vector2(0, -1),
            pygame.Vector2(0, 0),
        ]
        return random.choice(choices)

    def update(
        self,
        dt: float,
        target_pos: Tuple[float, float],
        bullets: pygame.sprite.Group,
        bullet_images: Dict[str, pygame.Surface],
        now_ms: int,
    ) -> None:
        self._decision_timer -= dt
        target_vec = pygame.Vector2(target_pos)
        if self._decision_timer <= 0:
            self._direction = self._pick_direction(target_vec)
            self._decision_timer = random.uniform(0.35, 0.9)
        previous_center = self.tank.rect.center
        self.tank.move(self._direction, dt)
        if self.tank.rect.center == previous_center and self._direction.length_squared() > 0:
            self._decision_timer = 0
        aligned_horizontally = abs(self.tank.rect.centery - target_vec.y) <= 18
        aligned_vertically = abs(self.tank.rect.centerx - target_vec.x) <= 18
        should_fire = False
        if aligned_horizontally and self.tank.orientation in {"left", "right"}:
            should_fire = True
        elif aligned_vertically and self.tank.orientation in {"up", "down"}:
            should_fire = True
        elif random.random() < 0.008:
            should_fire = True
        if should_fire and self.tank.can_fire(now_ms):
            self.tank.shoot(bullet_images, bullets, now_ms)


def draw_playfield(surface: pygame.Surface, area: pygame.Rect) -> None:
    surface.fill(COLOR_BACKGROUND)
    border_color = (52, 56, 68)
    inner_color = (32, 36, 46)
    pygame.draw.rect(surface, border_color, area.inflate(12, 12), border_radius=4, width=6)
    cell = PIXEL_SIZE * 5
    for x in range(area.left, area.right, cell):
        pygame.draw.line(surface, inner_color, (x, area.top), (x, area.bottom), 1)
    for y in range(area.top, area.bottom, cell):
        pygame.draw.line(surface, inner_color, (area.left, y), (area.right, y), 1)


def handle_player_input(player: Tank, keys: Iterable[bool], dt: float) -> None:
    direction = pygame.Vector2(0, 0)
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        direction.x -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        direction.x += 1
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        direction.y -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        direction.y += 1
    player.move(direction, dt)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Pixel Tank Battle")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 22)

    playfield = pygame.Rect(48, 48, WINDOW_SIZE[0] - 96, WINDOW_SIZE[1] - 96)

    player_images = create_tank_images(PLAYER_TANK_PATTERN, PLAYER_TANK_PALETTE, PIXEL_SIZE)
    enemy_images = create_tank_images(ENEMY_TANK_PATTERN, ENEMY_TANK_PALETTE, PIXEL_SIZE)
    bullet_images = create_bullet_images(BULLET_PATTERN, BULLET_PALETTE, PIXEL_SIZE)

    player = Tank(player_images, (playfield.left + 70, playfield.bottom - 70), speed=140.0, playfield=playfield)
    enemy = Tank(enemy_images, (playfield.right - 70, playfield.top + 70), speed=110.0, playfield=playfield)
    enemy_ai = EnemyController(enemy)

    tanks = pygame.sprite.Group(player, enemy)
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    running = True
    state = "playing"

    while running:
        dt = clock.tick(FPS) / 1000.0
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if state == "playing":
            handle_player_input(player, keys, dt)
            if keys[pygame.K_SPACE] or keys[pygame.K_LCTRL]:
                player.shoot(bullet_images, player_bullets, now_ms)

            enemy_ai.update(dt, player.rect.center, enemy_bullets, bullet_images, now_ms)

            player_bullets.update(dt)
            enemy_bullets.update(dt)

            if bullet_hits(enemy, player_bullets):
                if enemy.take_hit():
                    enemy.kill()
                    state = "victory"

            if bullet_hits(player, enemy_bullets):
                if player.take_hit():
                    player.kill()
                    state = "defeat"

        draw_playfield(screen, playfield)
        tanks.draw(screen)
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)

        hud_color = (218, 218, 218)
        player_text = font.render(f"Player HP: {max(player.health, 0)}", True, hud_color)
        enemy_text = font.render(f"Enemy HP: {max(enemy.health, 0)}", True, hud_color)
        screen.blit(player_text, (playfield.left, playfield.bottom + 12))
        screen.blit(enemy_text, (playfield.left, playfield.bottom + 12 + player_text.get_height() + 4))

        if state == "victory":
            message = font.render("Victory! Press ESC to quit", True, hud_color)
            screen.blit(message, message.get_rect(center=(WINDOW_SIZE[0] // 2, 36)))
        elif state == "defeat":
            message = font.render("Defeat... Press ESC to quit", True, hud_color)
            screen.blit(message, message.get_rect(center=(WINDOW_SIZE[0] // 2, 36)))

        pygame.display.flip()

        if state != "playing" and (keys[pygame.K_ESCAPE] or keys[pygame.K_q]):
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
