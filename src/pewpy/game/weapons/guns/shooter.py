"""What carries a gun: what a gun needs to know about it, this frame."""

from collections.abc import Callable
from dataclasses import dataclass, field

from pewpy.game.entities import Entity

# Makes an enemy of a kind at (x, y), heading that way (radians, None: its own) with its first timer (None: its own).
Maker = Callable[[str, float, float, float | None, float | None], Entity]


def _no_maker(kind: str, _x: float, _y: float, _heading: float | None, _timer: float | None) -> Entity:
    raise NoMakerError(kind)


class NoMakerError(Exception):
    """A gun tried to launch an enemy with nothing to make it."""

    def __init__(self, kind: str) -> None:
        super().__init__(f"this gun can't launch a {kind!r}: nothing to make it")


@dataclass
class Shooter:
    """What a gun needs to know about what carries it, this frame."""

    piece: Entity  # where it fires from (an enemy, a boss's part, the player's ship)
    target: Entity | None  # what it aims at (the player, for enemies), if anything
    age: float = 0.0  # of the enemy, for sweeping guns
    clock: float = 0.0  # seconds in the enemy's state
    remaining: float = 0.0  # seconds left in the enemy's state (its timer)
    on_screen: bool = True
    make: Maker = _no_maker
    stop: Callable[[], None] = field(default=lambda: None)  # stand still (a gun that holds)
    hostile: bool = True  # its shots hurt the player (else the enemies)
    forward: int = -1  # straight ahead: -1 down the screen (enemies), 1 up (the player)
    trigger: bool = True  # fire held (enemies always fire)
    mounts: dict[int, tuple[float, float]] = field(default_factory=dict)  # its model's weapons: (x, y) from its middle
    slot: int = 0  # which of its state's guns is firing (the first: 0), for picking a weapon (see Gun.weapons)
