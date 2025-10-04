"""Configuration constants and game settings."""

from typing import Dict, Tuple, Iterable

# Window and display settings
WINDOW_SIZE: Tuple[int, int] = (640, 480)
FPS = 60
PIXEL_SIZE = 4
COLOR_BACKGROUND = (18, 20, 26)

# Tank patterns and palettes
PLAYER_TANK_PATTERN = [
    "...11..11....",
    "...11..11....",
    "...111111....",
    "..111333111..",
    ".11133333111.",
    ".11223332211.",
    ".11223332211.",
    ".11233332211.",
    ".11233332211.",
    ".11223332211.",
    ".11133333111.",
    "..111333111..",
    ".11133333111.",
    "..111333111..",
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

# Bullet patterns and palettes
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

# Obstacle patterns and palettes
OBSTACLE_PATTERN = [
    "1111111111111111111111111",
    "1111111111111111111111111",
    "1111111111111111111111111",
    "1111111111111111111111111",
    "1111111111111111111111111",
    "1111111111111111111111111",
    "1111111111111111111111111",
    "1111111111111111111111111",
]

OBSTACLE_PALETTE: Dict[str, Tuple[int, int, int]] = {
    "1": (94, 84, 142),
}

# Tank settings
DEFAULT_TANK_HEALTH = 4
DEFAULT_TANK_RELOAD_MS = 450
PLAYER_TANK_SPEED = 140.0
ENEMY_TANK_SPEED = 110.0
BULLET_SPEED = 360.0

# Obstacle settings
DEFAULT_OBSTACLES = 6
OBSTACLE_SAFE_RADIUS = 80
OBSTACLE_MIN_DISTANCE = 100

# AI settings
AI_DECISION_MIN_TIME = 0.35
AI_DECISION_MAX_TIME = 0.9
AI_TARGET_SEEK_PROBABILITY = 0.6
AI_RANDOM_FIRE_PROBABILITY = 0.008

# Collision detection settings
COLLISION_PUSH_DISTANCE = 2
TANK_COLLISION_THRESHOLD = 35

# Spawn point settings
PLAYER_SPAWN_OFFSET_X = 70
PLAYER_SPAWN_OFFSET_Y = 70
ENEMY_SPAWN_OFFSET_X = 70
ENEMY_SPAWN_OFFSET_Y = 70