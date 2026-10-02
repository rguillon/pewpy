"""When a gun fires, each way in its own module: every `interval`, volleys included (volley.py), charging first
(charge.py), once at a time of its state (at.py), its volleys starting on the next frame (wait_volley.py) or during
a window of each interval (window.py). `step` runs a gun for a frame.
"""

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.laser import laser_beams
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import at, charge, wait_volley, window
from pewpy.game.weapons.guns.timing.volley import reloaded, start_volley, volley

__all__ = ["step"]


def step(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """Run `gun` for a frame: what it fired."""
    created: list[Entity] = []
    if state.charge > 0:
        state.charge -= dt
        if state.charge <= 0:
            created += laser_beams(state.item or gun, shooter.piece, warning=False)
    if state.beaming > 0 or state.charging > 0:
        return created + charge.step(gun, state, shooter, dt)
    if gun.window:
        return created + window.step(gun, state, shooter, dt)
    if gun.at is not None:
        return created + at.step(gun, state, shooter)
    if gun.wait_volley:
        return created + wait_volley.step(gun, state, shooter, dt)
    if reloaded(gun, state, shooter, dt):
        if gun.charge:
            state.charging = gun.charge
            if gun.hold:
                shooter.stop()
            return created
        start_volley(gun, state)
    return created + volley(state, shooter, dt)
