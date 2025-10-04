"""Pixel art rendering and graphics creation functions."""

from typing import Dict, Iterable, Tuple
import pygame

from config import (
    PIXEL_SIZE,
    COLOR_BACKGROUND,
    PLAYER_TANK_PATTERN,
    ENEMY_TANK_PATTERN,
    PLAYER_TANK_PALETTE,
    ENEMY_TANK_PALETTE,
    BULLET_PATTERN,
    BULLET_PALETTE,
    OBSTACLE_PATTERN,
    OBSTACLE_PALETTE,
)


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
    """Create directional tank images from a base pattern."""
    base = create_pixel_surface(pattern, palette, pixel_size)
    return {
        "up": base,
        "right": pygame.transform.rotate(base, -90),
        "down": pygame.transform.rotate(base, 180),
        "left": pygame.transform.rotate(base, 90),
    }


def create_bullet_images(pattern: Iterable[str], palette: Dict[str, Tuple[int, int, int]], pixel_size: int) -> Dict[str, pygame.Surface]:
    """Create directional bullet images from a base pattern."""
    base = create_pixel_surface(pattern, palette, pixel_size)
    return {
        "up": base,
        "right": pygame.transform.rotate(base, -90),
        "down": pygame.transform.rotate(base, 180),
        "left": pygame.transform.rotate(base, 90),
    }


def create_obstacle_image(pattern: Iterable[str], palette: Dict[str, Tuple[int, int, int]], pixel_size: int) -> pygame.Surface:
    """Create an obstacle image from a pattern."""
    return create_pixel_surface(pattern, palette, pixel_size)


def get_bullet_spawn_offset(tank_rect: pygame.Rect, orientation: str, bullet_images: Dict[str, pygame.Surface]) -> Tuple[int, int]:
    """Calculate the spawn offset for bullets based on tank orientation."""
    if orientation == "up":
        offset_x, offset_y = 0, bullet_images["up"].get_height() // 2
    elif orientation == "down":
        offset_x, offset_y = 0, -bullet_images["down"].get_height() // 2
    elif orientation == "left":
        offset_x, offset_y = bullet_images["left"].get_width() // 2, 0
    else:  # right
        offset_x, offset_y = -bullet_images["right"].get_width() // 2, 0

    return offset_x, offset_y


def orientation_from_vector(direction: pygame.Vector2) -> str:
    """Return the closest cardinal orientation string from a vector."""
    if direction.length_squared() == 0:
        return "up"
    if abs(direction.x) > abs(direction.y):
        return "right" if direction.x > 0 else "left"
    return "down" if direction.y > 0 else "up"


def draw_playfield(surface: pygame.Surface, area: pygame.Rect) -> None:
    """Draw the game playfield with border and grid."""
    surface.fill(COLOR_BACKGROUND)
    border_color = (52, 56, 68)
    inner_color = (32, 36, 46)
    pygame.draw.rect(surface, border_color, area.inflate(12, 12), border_radius=4, width=6)
    cell = PIXEL_SIZE * 5
    for x in range(area.left, area.right, cell):
        pygame.draw.line(surface, inner_color, (x, area.top), (x, area.bottom), 1)
    for y in range(area.top, area.bottom, cell):
        pygame.draw.line(surface, inner_color, (area.left, y), (area.right, y), 1)


def create_game_images() -> Tuple[Dict[str, pygame.Surface], Dict[str, pygame.Surface], Dict[str, pygame.Surface], pygame.Surface]:
    """Create all game images and return them."""
    player_images = create_tank_images(PLAYER_TANK_PATTERN, PLAYER_TANK_PALETTE, PIXEL_SIZE)
    enemy_images = create_tank_images(ENEMY_TANK_PATTERN, ENEMY_TANK_PALETTE, PIXEL_SIZE)
    bullet_images = create_bullet_images(BULLET_PATTERN, BULLET_PALETTE, PIXEL_SIZE)
    obstacle_image = create_obstacle_image(OBSTACLE_PATTERN, OBSTACLE_PALETTE, PIXEL_SIZE)

    return player_images, enemy_images, bullet_images, obstacle_image