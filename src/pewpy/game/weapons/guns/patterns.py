"""One shot of a gun: its pattern's bullets (or enemies, or beam), from each of its origins."""

import math

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import beam
from pewpy.game.weapons.guns.gun import Gun, distance
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
    for x, y in gun.origins:
        ox, oy = distance(x, piece.width, piece.height), distance(y, piece.width, piece.height)
        muzzle = piece if ox == 0 and oy == 0 else Entity(x=piece.x + ox, y=piece.y + oy)
        if gun.pattern == "beam":
            created.append(beam(muzzle.x, muzzle.y, gun.width, gun.duration))
            continue
        if gun.velocities:
            created += [styled_bullet(gun, muzzle, vx, vy, shooter.hostile) for vx, vy in gun.velocities]
            continue
        target = shooter.target or muzzle
        if angle is not None:
            angles = [angle]
        else:
            angles = pattern_angles(gun, muzzle, target, turned, shooter.age, shooter.forward)
        extra = gun.volley_angles[index % len(gun.volley_angles)] if gun.volley_angles else 0.0
        for number, direction in enumerate(angles):
            direction += extra
            speed = gun.speeds[number % len(gun.speeds)] if gun.speeds else gun.speed
            if gun.spawn or gun.projectile:
                created.append(launch(gun, muzzle, direction, ox, shooter))
            else:
                radians = math.radians(direction)
                vx, vy = math.sin(radians) * speed, shooter.forward * math.cos(radians) * speed
                created.append(styled_bullet(gun, muzzle, vx, vy, shooter.hostile))
    return created


def pattern_angles(
    gun: Gun, source: Entity, target: Entity, turned: float, age: float, forward: int = -1
) -> list[float]:
    """The directions of one shot's bullets, in degrees from straight ahead (`forward`: -1 down, 1 up)."""
    if gun.pattern == "aimed":
        middle = math.degrees(math.atan2(target.x - source.x, forward * (target.y - source.y)))
    else:
        middle = gun.sweep * math.sin(2 * math.pi * age / SWEEP_PERIOD)
    if gun.angles:
        return [middle + turned + gun.angle + angle for angle in gun.angles]
    if gun.pattern == "ring":
        return [middle + turned + gun.angle + index * 360 / gun.count for index in range(gun.count)]
    return [middle + turned + gun.angle + (index - (gun.count - 1) / 2) * gun.spread for index in range(gun.count)]
