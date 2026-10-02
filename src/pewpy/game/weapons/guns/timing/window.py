"""A gun with a `window`: it fires in bursts, one in each `interval` of the state.

It fires every `gap` seconds during the first `window` seconds of each interval, sweeping from `-reach` to `reach`
degrees (the other way round every other time).
"""

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.patterns import fire
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState


def step(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """Fire every `gap` seconds while in the window, sweeping."""
    into = shooter.clock % gun.interval
    if into >= gun.window:
        return []
    state.volley_timer -= dt
    if state.volley_timer > 0:
        return []
    state.volley_timer = gun.gap
    forward = int(shooter.clock // gun.interval) % 2 == 0
    angle = (into / gun.window * 2 - 1) * gun.reach * (1 if forward else -1)
    return fire(gun, shooter, state, angle)
