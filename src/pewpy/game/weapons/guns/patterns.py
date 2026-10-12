"""One shot of a gun: its pattern's bullets (or enemies, or beam), from each of its origins."""

import math

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import beam
from pewpy.game.weapons.guns.gun import MIDDLE, Gun, distance
from pewpy.game.weapons.guns.launch import launch
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.styles import styled_bullet

SWEEP_PERIOD = 2.0  # seconds for a sweeping gun to go from one side to the other and back


def fire(gun: Gun, shooter: Shooter, state: GunState | None = None, angle: float | None = None) -> list[Entity]:
    """One shot of `gun` from each of its origins: its bullets (or enemies, or beam), all at the same time."""
    turned = state.turned if state else 0.0
    index = state.volley_index if state else 0
    piece = shooter.piece
    created: list[Entity] = []
    if gun.pattern in ("ray", "chain"):
        return created  # played out by what carries it (see pewpy.game.weapons.guns)
    for ox, oy, depth in origins(gun, shooter):
        muzzle = piece if ox == 0 and oy == 0 else Entity(x=piece.x + ox, y=piece.y + oy)
        if gun.pattern == "beam":
            created.append(beam(muzzle.x, muzzle.y, gun.width, gun.duration, depth))
            continue
        if gun.velocities:
            created += [styled_bullet(gun, muzzle, vx, vy, shooter.hostile, depth) for vx, vy in gun.velocities]
            continue
        target = shooter.target or muzzle
        if angle is not None:
            angles = [angle]
        else:
            angles = pattern_angles(gun, muzzle, target, turned, shooter.age, shooter.forward)
        extra = gun.volley_angles[index % len(gun.volley_angles)] if gun.volley_angles else 0.0
        for number, direction in enumerate([a + extra for a in angles]):
            speed = gun.speeds[number % len(gun.speeds)] if gun.speeds else gun.speed
            if gun.spawn or gun.projectile:
                created.append(launch(gun, muzzle, direction, ox, shooter))
            else:
                radians = math.radians(direction)
                vx, vy = math.sin(radians) * speed, shooter.forward * math.cos(radians) * speed
                created.append(styled_bullet(gun, muzzle, vx, vy, shooter.hostile, depth))
    return created


def origins(gun: Gun, shooter: Shooter) -> list[tuple[float, float, float]]:
    """Return where a gun's shots come out: (x, y) from the middle of what carries it, and the muzzle's depth.

    See Gun.origins and Gun.weapons; an origin that isn't a weapon is on the play plane (depth 0).
    """
    if gun.weapons:
        mounts = [shooter.mounts[number] for number in gun.weapons]
    elif shooter.mounts and gun.origins == MIDDLE:
        numbers = sorted(shooter.mounts)
        mounts = [shooter.mounts[numbers[shooter.slot % len(numbers)]]]
    else:
        piece = shooter.piece
        return [
            (distance(x, piece.width, piece.height), distance(y, piece.width, piece.height), 0.0)
            for x, y in gun.origins
        ]
    return [(mount.x, mount.y, mount.depth) for mount in mounts]


def pattern_angles(
    gun: Gun, source: Entity, target: Entity, turned: float, age: float, forward: int = -1
) -> list[float]:
    """Return the directions of one shot's bullets, in degrees from straight ahead (`forward`: -1 down, 1 up)."""
    if gun.pattern == "aimed":
        middle = math.degrees(math.atan2(target.x - source.x, forward * (target.y - source.y)))
    else:
        middle = gun.sweep * math.sin(2 * math.pi * age / SWEEP_PERIOD)
    if gun.angles:
        return [middle + turned + gun.angle + angle for angle in gun.angles]
    if gun.pattern == "ring":
        return [middle + turned + gun.angle + index * 360 / gun.count for index in range(gun.count)]
    return [middle + turned + gun.angle + (index - (gun.count - 1) / 2) * gun.spread for index in range(gun.count)]
