"""A gun with `charge` (glowing before it fires), or a "beam" gun firing its beam."""

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.patterns import fire
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState


def step(gun: Gun, state: GunState, shooter: Shooter, dt: float) -> list[Entity]:
    """Glowing before it fires, or firing its beam."""
    if state.beaming > 0:
        state.beaming -= dt
        return []
    state.charging -= dt
    if state.charging > 0:
        return []
    if gun.pattern == "beam":
        state.beaming = gun.duration
    return fire(gun, shooter, state)
