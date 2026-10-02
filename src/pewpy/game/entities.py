"""Base game objects, independent from rendering."""

from dataclasses import dataclass

from pewpy import config


@dataclass(eq=False)
class Entity:
    """A moving rectangle. Positions are world units, (0, 0) is the center of the play area."""

    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    width: float = 0.1
    height: float = 0.1
    alive: bool = True

    def move(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def overlaps(self, other: "Entity") -> bool:
        return (
            abs(self.x - other.x) < (self.width + other.width) / 2
            and abs(self.y - other.y) < (self.height + other.height) / 2
        )

    def in_play_area(
        self, margin: float = 0.2, top: float = config.PLAY_HEIGHT / 2, side: float = config.PLAY_WIDTH / 2
    ) -> bool:
        """Within `margin` of the area from -side to side across and from the bottom of the play area to `top`."""
        return abs(self.x) < side + margin and -config.PLAY_HEIGHT / 2 - margin < self.y < top + margin


@dataclass(eq=False)
class Pickup(Entity):
    """Dropped by enemies: an upgrade capsule for a weapon ("bullets", "laser", "missiles"), a "repair", an extra
    "life" or a secondary weapon ("turret", "lightning").
    """

    kind: str = "repair"
    vy: float = -config.PICKUP_SPEED
    width: float = config.PICKUP_SIZE
    height: float = config.PICKUP_SIZE
