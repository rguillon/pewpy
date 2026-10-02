"""Guns launching enemies instead of bullets: a boss's `projectile`, or any `spawn`."""

import math

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.shooter import Shooter

# A boss gun's `projectile`: the enemy it launches, and how fast (a homing missile sets its own speed).
PROJECTILES = {"rocket": ("rocket", 0.25), "missile": ("homing_missile", 0.0), "cluster": ("cluster_bomb", 0.3)}


def launch(gun: Gun, muzzle: Entity, direction: float, ox: float, shooter: Shooter) -> Entity:
    """The enemy `gun` launches from `muzzle` (`ox` across from the middle of what carries it), `direction`
    degrees from straight ahead.
    """
    kind, speed = PROJECTILES[gun.projectile] if gun.projectile else (gun.spawn, gun.spawn_speed)
    heading = math.radians(gun.spawn_heading) if gun.spawn_heading is not None else None
    vx = vy = fuse = None
    if speed is not None:
        radians = math.radians(direction)
        dx, dy = math.sin(radians), shooter.forward * math.cos(radians)
        vx, vy = dx * speed, dy * speed
        heading = math.atan2(dy, dx) if heading is None else heading
        if gun.spawn_fuse and speed and shooter.target:
            fuse = math.hypot(shooter.target.x - muzzle.x, shooter.target.y - muzzle.y) / speed
    elif gun.spawn_velocity is not None:
        vx, vy = gun.spawn_velocity
        vx = math.copysign(vx, ox) if ox else vx
    enemy = shooter.make(kind, muzzle.x, muzzle.y, heading, fuse)
    if vx is not None and vy is not None:
        enemy.vx, enemy.vy = vx, vy
    return enemy
