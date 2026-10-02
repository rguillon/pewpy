"""The bullets a gun fires, by its style (or kind): see Gun.style and pewpy.game.weapons.bullets."""

import math

from pewpy import config
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import AccelBullet, Bullet, CurveBullet, Missile, WaveBullet
from pewpy.game.weapons.guns.gun import Gun

HEAVY_BULLET_SIZE = 0.05  # "heavy" shots: bigger and orange (the hitbox too)
BULLET_SIZES = {"heavy": HEAVY_BULLET_SIZE, "pellet": 0.022}  # the others are config.ENEMY_BULLET_SIZE
ACCEL_START = 0.35  # "accel" shots start at this share of their speed...
ACCEL_RATE = 0.9  # ...and speed up by this much per second...
ACCEL_TOP = 1.8  # ...up to this many times their speed


def styled_bullet(gun: Gun, source: Entity, vx: float, vy: float, hostile: bool = True) -> Bullet:
    """Make a bullet of the gun's style (or kind) from `source`, flying at (vx, vy) (an "accel" one starts slower)."""
    if gun.bullet == "missile":
        bullet: Bullet = Missile(
            homing=gun.homing > 0,
            turn_rate=math.radians(gun.homing),
            splash_damage=gun.splash,
            splash_radius=gun.splash_radius,
        )
    elif gun.style == "wave":
        bullet = WaveBullet()
    elif gun.style == "accel":
        bullet = AccelBullet(rate=ACCEL_RATE * gun.speed, top_speed=ACCEL_TOP * gun.speed)
        vx, vy = vx * ACCEL_START, vy * ACCEL_START
    elif gun.style == "curve":
        bullet = CurveBullet(turn_rate=gun.curve)
    else:
        bullet = Bullet()
    bullet.x, bullet.y, bullet.vx, bullet.vy = source.x, source.y, vx, vy
    if gun.size is None:
        bullet.width = bullet.height = BULLET_SIZES.get(gun.style, config.ENEMY_BULLET_SIZE)
    else:
        bullet.width, bullet.height = gun.size
    bullet.damage = config.ENEMY_BULLET_DAMAGE if gun.damage is None else gun.damage
    bullet.hostile, bullet.style = hostile, gun.style
    return bullet
