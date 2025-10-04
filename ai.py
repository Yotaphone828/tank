"""AI system for enemy tank behavior."""

import random
from typing import Iterable, Tuple
import pygame

from config import (
    AI_DECISION_MIN_TIME,
    AI_DECISION_MAX_TIME,
    AI_TARGET_SEEK_PROBABILITY,
    AI_RANDOM_FIRE_PROBABILITY,
)


class EnemyController:
    """Lightweight AI that drives the enemy tank."""

    def __init__(self, tank: "entities.Tank") -> None:
        self.tank = tank
        self._direction = pygame.Vector2(0, -1)
        self._decision_timer = 0.0

    def _pick_direction(self, target_pos: pygame.Vector2) -> pygame.Vector2:
        """Pick movement direction with target-seeking behavior."""
        if random.random() < AI_TARGET_SEEK_PROBABILITY:
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
        bullet_images: dict,
        now_ms: int,
        blockers: Iterable[pygame.sprite.Sprite] | None = None,
    ) -> None:
        """Update AI behavior including movement and shooting."""
        self._decision_timer -= dt
        target_vec = pygame.Vector2(target_pos)
        if self._decision_timer <= 0:
            self._direction = self._pick_direction(target_vec)
            self._decision_timer = random.uniform(AI_DECISION_MIN_TIME, AI_DECISION_MAX_TIME)

        previous_center = self.tank.rect.center
        self.tank.move(self._direction, dt, blockers=blockers)
        if self.tank.rect.center == previous_center and self._direction.length_squared() > 0:
            self._decision_timer = 0

        aligned_horizontally = abs(self.tank.rect.centery - target_vec.y) <= 18
        aligned_vertically = abs(self.tank.rect.centerx - target_vec.x) <= 18
        should_fire = False
        if aligned_horizontally and self.tank.orientation in {"left", "right"}:
            should_fire = True
        elif aligned_vertically and self.tank.orientation in {"up", "down"}:
            should_fire = True
        elif random.random() < AI_RANDOM_FIRE_PROBABILITY:
            should_fire = True

        if should_fire and self.tank.can_fire(now_ms):
            self.tank.shoot(bullet_images, bullets, now_ms)