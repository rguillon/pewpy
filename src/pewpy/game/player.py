"""Player ship logic, independent from rendering. The ships the player can pick are in `data/ships.json`."""

import json
import math
from dataclasses import dataclass, field

from pewpy import config
from pewpy.data import data_folder
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class ShipSpec:
    """A ship the player can pick (see 01-gameplay.md, "Player ships")."""

    name: str
    description: str  # a few words, shown on the ship selection screen
    drawing: str  # its model: models/<drawing>.json
    health: float  # a full health bar
    speed: float  # top speed, world units per second
    size: float  # the hitbox, a square; the model is about as big
    regeneration: float = 0.0  # health repaired per second while not firing (after `regeneration_delay`)
    regeneration_delay: float = 0.0  # seconds without firing before repairs start


def load_ships() -> dict[str, ShipSpec]:
    """The ships of `ships.json`, by name, in the file's order (a ship's "note" is for the people editing it)."""
    data = json.loads((data_folder() / "ships.json").read_text())
    return {key: ShipSpec(**{k: v for k, v in ship.items() if k != "note"}) for key, ship in data.items()}


SHIPS = load_ships()
DEFAULT_SHIP = next(iter(SHIPS))  # the first one


@dataclass(eq=False)
class Player(Entity):
    """The player's ship: its size, health and speed come from its ShipSpec."""

    ship: ShipSpec = field(default_factory=lambda: SHIPS[DEFAULT_SHIP])
    y: float = config.PLAYER_START_Y
    health: float = 0.0  # starts full, see __post_init__
    invulnerable_time: float = 0.0
    since_fired: float = 0.0  # seconds since the ship last fired (self-repairing ships wait for it)

    def __post_init__(self) -> None:
        self.width = self.height = self.ship.size
        self.health = self.ship.health

    def update(self, dt: float, move_x: float, move_y: float, firing: bool = False) -> None:
        """Advance the ship by `dt` seconds.

        Args:
            dt: Elapsed time in seconds.
            move_x: Horizontal input, -1 (left) to 1 (right).
            move_y: Vertical input, -1 (down) to 1 (up).
            firing: Whether the fire button is held (self-repairing ships only repair when it isn't).

        """
        self.invulnerable_time = max(0.0, self.invulnerable_time - dt)
        self.since_fired = 0.0 if firing else self.since_fired + dt
        if self.ship.regeneration and self.since_fired >= self.ship.regeneration_delay and self.health > 0:
            self.health = min(self.ship.health, self.health + self.ship.regeneration * dt)

        length = math.hypot(move_x, move_y)
        if length > 1.0:
            move_x, move_y = move_x / length, move_y / length

        # Ease velocity towards the target speed: a little inertia, independent of frame rate.
        blend = 1.0 - math.exp(-config.PLAYER_RESPONSIVENESS * dt)
        self.vx += (move_x * self.ship.speed - self.vx) * blend
        self.vy += (move_y * self.ship.speed - self.vy) * blend

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
