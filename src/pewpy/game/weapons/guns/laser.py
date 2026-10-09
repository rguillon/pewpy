"""A boss's "laser" gun: beams straight down that follow it, each announced by a thin harmless beam."""

from pewpy import config
from pewpy.game.enemies.mounts import Mount
from pewpy.game.weapons.bullets import BossBeam, Bullet
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.shooter import Shooter

LASER_WARNING = 1.0  # seconds of thin harmless beam before a laser fires: time to move away
WARNING_WIDTH = 0.008
LASER_KINDS = ("laser", "cannon")  # the weapons a laser fires from first, in that order (then any other)


def laser_beams(gun: Gun, shooter: Shooter, warning: bool) -> list[Bullet]:
    """Make a laser gun's beams from what carries it, or their thin harmless warnings."""
    beams: list[Bullet] = []
    for offset_x, offset_y, depth in beam_origins(gun, shooter):
        laser = BossBeam(
            width=WARNING_WIDTH if warning else gun.width,
            damage=0.0 if warning else config.ENEMY_BULLET_DAMAGE,
            hostile=True,
            style="warning" if warning else "beam",
            life=LASER_WARNING if warning else gun.duration,
            pierces=True,
            harmless=warning,
            source=shooter.piece,
            offset_x=offset_x,
            offset_y=offset_y,
            depth=depth,
        )
        laser.move(0.0)  # in place under its source
        beams.append(laser)
    return beams


def beam_origins(gun: Gun, shooter: Shooter) -> list[tuple[float, float | None, float]]:
    """Return where a laser's beams start: (x, y) from the middle of what carries it, and their depth.

    From the weapons it names; else, on a model with weapons, one beam from the weapon nearest each of its `offsets`
    (its laser weapons first, then its cannons, then any: each weapon fires one beam); else from under its middle, at
    each of its `offsets`, on the play plane (y None: under it).
    """
    if gun.weapons:
        return [_start(shooter.mounts[number]) for number in gun.weapons]
    if not shooter.mounts:
        return [(offset, None, 0.0) for offset in gun.offsets]
    mounts = list(shooter.mounts.values())
    for kind in LASER_KINDS:
        if any(mount.kind == kind for mount in mounts):
            mounts = [mount for mount in mounts if mount.kind == kind]
            break
    picked: list[Mount] = []
    for offset in gun.offsets:
        left = [mount for mount in mounts if mount not in picked]
        if left:
            picked.append(min(left, key=lambda mount: abs(mount.x - offset)))
    return [_start(mount) for mount in picked]


def _start(mount: Mount) -> tuple[float, float, float]:
    return mount.x, mount.y, mount.depth
