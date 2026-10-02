"""A gun with `at`: it fires once, when its state has that many seconds left."""

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.patterns import fire
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState


def step(gun: Gun, state: GunState, shooter: Shooter) -> list[Entity]:
    if state.fired or shooter.remaining > (gun.at or 0.0):
        return []
    state.fired = True
    return fire(gun, shooter, state)
