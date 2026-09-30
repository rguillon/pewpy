"""Player ship logic, independent from rendering."""

import math
from dataclasses import dataclass

from pewpy import config
from pewpy.entities import Entity


@dataclass(eq=False)
class Player(Entity):
    """The player's ship."""

    y: float = config.PLAYER_START_Y
    width: float = config.PLAYER_WIDTH
    height: float = config.PLAYER_HEIGHT
    health: float = config.PLAYER_HEALTH
    invulnerable_time: float = 0.0

    def update(self, dt: float, move_x: float, move_y: float) -> None:
        """Advance the ship by `dt` seconds.

        Args:
            dt: Elapsed time in seconds.
            move_x: Horizontal input, -1 (left) to 1 (right).
            move_y: Vertical input, -1 (down) to 1 (up).
        """
        self.invulnerable_time = max(0.0, self.invulnerable_time - dt)

        length = math.hypot(move_x, move_y)
        if length > 1.0:
            move_x, move_y = move_x / length, move_y / length

        # Ease velocity towards the target speed: a little inertia, independent of frame rate.
        blend = 1.0 - math.exp(-config.PLAYER_RESPONSIVENESS * dt)
        self.vx += (move_x * config.PLAYER_SPEED - self.vx) * blend
        self.vy += (move_y * config.PLAYER_SPEED - self.vy) * blend

        self.move(dt)
        self._clamp_to_play_area()

    @property
    def invulnerable(self) -> bool:
        return self.invulnerable_time > 0

    def take_hit(self, damage: float) -> None:
        self.health -= damage
        self.invulnerable_time = config.PLAYER_INVULNERABILITY_TIME

    def _clamp_to_play_area(self) -> None:
        max_x = (config.PLAY_WIDTH - self.width) / 2
        max_y = (config.PLAY_HEIGHT - self.height) / 2
        if abs(self.x) > max_x:
            self.x = math.copysign(max_x, self.x)
            self.vx = 0.0
        if abs(self.y) > max_y:
            self.y = math.copysign(max_y, self.y)
            self.vy = 0.0
