"""A gun with `wait_volley`."""

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing.volley import reloaded, shoot, start_volley, volley


def step(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """No reloading during a volley, which starts on the next frame (a volley of one fires at once)."""
    if state.volley_left > 0:
        return volley(state, shooter, dt)
    if not reloaded(gun, state, shooter, dt):
        return []
    item = start_volley(gun, state)
    if item.volley > 1:
        return []
    state.volley_left = 0
    return shoot(item, state, shooter)
