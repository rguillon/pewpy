"""A boss's "laser" gun: beams straight down that follow it, each announced by a thin harmless beam."""

from pewpy import config
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import BossBeam, Bullet
from pewpy.game.weapons.guns.gun import Gun

LASER_WARNING = 1.0  # seconds of thin harmless beam before a laser fires: time to move away
WARNING_WIDTH = 0.008


def laser_beams(gun: Gun, source: Entity, warning: bool) -> list[Bullet]:
    """Make a laser gun's beams from `source`, or their thin harmless warnings."""
    beams: list[Bullet] = []
    for offset in gun.offsets:
        laser = BossBeam(
            width=WARNING_WIDTH if warning else gun.width,
            damage=0.0 if warning else config.ENEMY_BULLET_DAMAGE,
            hostile=True,
            style="warning" if warning else "beam",
            life=LASER_WARNING if warning else gun.duration,
            pierces=True,
            harmless=warning,
            source=source,
            offset_x=offset,
        )
        laser.move(0.0)  # in place under its source
        beams.append(laser)
    return beams
