"""A shooter high on the screen aiming straight down, and running a gun frame by frame."""

import math

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import Gun, GunState, Shooter, step

DT = 1 / 60
BELOW = Entity(x=0.0, y=-0.8)  # a target straight down the screen
SOURCE = Entity(x=0.0, y=0.5)


def shooter(
    piece: Entity = SOURCE, target: Entity = BELOW, on_screen: bool = True, clock: float = 0.0, remaining: float = 0.0
) -> Shooter:
    """Make a shooter able to launch enemies."""
    return Shooter(piece, target, 0.0, clock, remaining, on_screen, Enemy.of_kind)


def degrees(bullet: Entity) -> float:
    """Its direction, in degrees from straight down."""
    return math.degrees(math.atan2(bullet.vx, -bullet.vy))


def frames(gun: Gun, seconds: float, aim: Shooter | None = None, state: GunState | None = None) -> list[int]:
    """Return the frames the gun fires on, over `seconds`."""
    aim = aim or shooter()
    state = state or GunState(cooldown=gun.delay)
    return [frame for frame in range(round(seconds / DT)) if step(gun, state, aim, DT)]
