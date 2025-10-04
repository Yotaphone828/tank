"""Core game logic and main game loop."""

import math
import random
from typing import Tuple
import pygame

from config import (
    WINDOW_SIZE,
    COLOR_BACKGROUND,
    PLAYER_SPAWN_OFFSET_X,
    PLAYER_SPAWN_OFFSET_Y,
    ENEMY_SPAWN_OFFSET_X,
    ENEMY_SPAWN_OFFSET_Y,
    DEFAULT_OBSTACLES,
    OBSTACLE_SAFE_RADIUS,
    OBSTACLE_MIN_DISTANCE,
)
from graphics import create_game_images, draw_playfield
from entities import Tank, Obstacle
from ai import EnemyController


def bullet_hits(target: Tank, projectiles: pygame.sprite.Group) -> bool:
    """Check if any projectile has struck the given tank."""
    collisions = pygame.sprite.spritecollide(target, projectiles, dokill=True)
    return bool(collisions)


def is_position_clear(position: Tuple[int, int], obstacles: pygame.sprite.Group,
                     player_pos: Tuple[int, int], enemy_pos: Tuple[int, int],
                     safe_radius: int = OBSTACLE_SAFE_RADIUS) -> bool:
    """Check if a position is clear of obstacles and away from spawn points."""
    # Check distance from player spawn point
    if math.sqrt((position[0] - player_pos[0])**2 + (position[1] - player_pos[1])**2) < safe_radius:
        return False

    # Check distance from enemy spawn point
    if math.sqrt((position[0] - enemy_pos[0])**2 + (position[1] - enemy_pos[1])**2) < safe_radius:
        return False

    # Check distance from existing obstacles
    temp_obstacle = Obstacle(pygame.Surface((32, 32)), position)
    for obstacle in obstacles:
        if temp_obstacle.rect.colliderect(obstacle.rect):
            return False

    return True


def generate_random_obstacles(obstacle_image: pygame.Surface, playfield: pygame.Rect,
                            player_pos: Tuple[int, int], enemy_pos: Tuple[int, int],
                            num_obstacles: int = DEFAULT_OBSTACLES) -> pygame.sprite.Group:
    """Generate randomly placed obstacles with good distribution."""
    obstacles = pygame.sprite.Group()

    # Define spawn areas (avoiding the edges where tanks spawn)
    min_x = playfield.left + 100
    max_x = playfield.right - 100
    min_y = playfield.top + 100
    max_y = playfield.bottom - 100

    attempts = 0
    max_attempts = 1000

    while len(obstacles) < num_obstacles and attempts < max_attempts:
        # Generate random position within the spawn area
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)

        # Ensure obstacles are not too close to each other
        temp_obstacle = Obstacle(obstacle_image, (x, y))
        too_close = False

        for existing_obstacle in obstacles:
            if temp_obstacle.rect.colliderect(existing_obstacle.rect):
                too_close = True
                break

            # Check minimum distance between obstacles
            center_distance = math.sqrt((x - existing_obstacle.rect.centerx)**2 +
                                 (y - existing_obstacle.rect.centery)**2)
            if center_distance < OBSTACLE_MIN_DISTANCE:
                too_close = True
                break

        if not too_close and is_position_clear((x, y), obstacles, player_pos, enemy_pos):
            obstacles.add(temp_obstacle)

        attempts += 1

    return obstacles


def handle_player_input(player: Tank, keys, dt: float, blockers: list) -> None:
    """Handle player input and update tank movement."""
    direction = pygame.Vector2(0, 0)
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        direction.x -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        direction.x += 1
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        direction.y -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        direction.y += 1
    player.move(direction, dt, blockers=blockers)


class TankGame:
    """Main game class handling initialization and game loop."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pixel Tank Battle")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 22)
        self.state = "playing"

        # Create playfield
        self.playfield = pygame.Rect(48, 48, WINDOW_SIZE[0] - 96, WINDOW_SIZE[1] - 96)

        # Create game images
        self.player_images, self.enemy_images, self.bullet_images, self.obstacle_image = create_game_images()

        # Generate random obstacles with good distribution
        self.player_spawn = (self.playfield.left + PLAYER_SPAWN_OFFSET_X,
                           self.playfield.bottom - PLAYER_SPAWN_OFFSET_Y)
        self.enemy_spawn = (self.playfield.right - ENEMY_SPAWN_OFFSET_X,
                          self.playfield.top + ENEMY_SPAWN_OFFSET_Y)
        self.obstacles = generate_random_obstacles(self.obstacle_image, self.playfield,
                                                 self.player_spawn, self.enemy_spawn)

        # Create tanks and AI
        self.player = Tank(self.player_images, self.player_spawn,
                          speed=140.0, playfield=self.playfield)
        self.enemy = Tank(self.enemy_images, self.enemy_spawn,
                         speed=110.0, playfield=self.playfield)
        self.enemy_ai = EnemyController(self.enemy)

        # Create sprite groups
        self.tanks = pygame.sprite.Group(self.player, self.enemy)
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()

        self.running = True

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_game(self, dt: float, now_ms: int):
        """Update game state."""
        keys = pygame.key.get_pressed()

        # Handle player input
        blockers = list(self.tanks) + list(self.obstacles)
        handle_player_input(self.player, keys, dt, blockers)

        # Handle player shooting
        if keys[pygame.K_SPACE] or keys[pygame.K_LCTRL]:
            self.player.shoot(self.bullet_images, self.player_bullets, now_ms)

        # Update AI
        self.enemy_ai.update(dt, self.player.rect.center, self.enemy_bullets,
                           self.bullet_images, now_ms, blockers)

        # Update bullets
        self.player_bullets.update(dt)
        self.enemy_bullets.update(dt)

        # Check bullet collisions with obstacles
        pygame.sprite.groupcollide(self.player_bullets, self.obstacles, True, False)
        pygame.sprite.groupcollide(self.enemy_bullets, self.obstacles, True, False)

        # Check bullet hits on tanks
        if bullet_hits(self.enemy, self.player_bullets):
            if self.enemy.take_hit():
                self.enemy.kill()
                self.state = "victory"

        if bullet_hits(self.player, self.enemy_bullets):
            if self.player.take_hit():
                self.player.kill()
                self.state = "defeat"

    def render_game(self):
        """Render the game."""
        # Clear screen and draw playfield
        draw_playfield(self.screen, self.playfield)

        # Draw all sprites
        self.tanks.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.player_bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game state messages
        if self.state == "victory":
            self.draw_game_over("Victory! Press ESC to quit")
        elif self.state == "defeat":
            self.draw_game_over("Defeat... Press ESC to quit")

        pygame.display.flip()

    def draw_hud(self):
        """Draw game HUD with health information."""
        hud_color = (218, 218, 218)
        player_text = self.font.render(f"Player HP: {max(self.player.health, 0)}", True, hud_color)
        enemy_text = self.font.render(f"Enemy HP: {max(self.enemy.health, 0)}", True, hud_color)
        self.screen.blit(player_text, (self.playfield.left, self.playfield.bottom + 12))
        self.screen.blit(enemy_text, (self.playfield.left, self.playfield.bottom + 12 + player_text.get_height() + 4))

    def draw_game_over(self, message: str):
        """Draw game over message."""
        hud_color = (218, 218, 218)
        message_surface = self.font.render(message, True, hud_color)
        self.screen.blit(message_surface, message_surface.get_rect(center=(WINDOW_SIZE[0] // 2, 36)))

    def handle_input_after_game_over(self):
        """Handle input when game is over."""
        keys = pygame.key.get_pressed()
        if self.state != "playing" and (keys[pygame.K_ESCAPE] or keys[pygame.K_q]):
            self.running = False

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            now_ms = pygame.time.get_ticks()

            self.handle_events()

            if self.state == "playing":
                self.update_game(dt, now_ms)

            self.render_game()
            self.handle_input_after_game_over()

        pygame.quit()


def main():
    """Entry point for the game."""
    game = TankGame()
    game.run()


if __name__ == "__main__":
    main()