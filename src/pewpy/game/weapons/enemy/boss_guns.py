"""Bosses' guns (02-enemies-bosses.md): how each fires its bullets, projectiles or laser beams. Independent from
rendering.

Guns fire bullets of several kinds (see Gun.style), launch projectiles (rockets, homing missiles, cluster bombs) or
fire laser beams, each announced by a thin harmless beam LASER_WARNING seconds before.
"""

import math
from dataclasses import dataclass

from pewpy import config
from pewpy.game.entities import Bullet, Entity
from pewpy.game.weapons.enemy.projectiles import ClusterBomb, HomingMissile, Rocket
from pewpy.game.weapons.enemy.shots import BEAM_BOTTOM, HEAVY_BULLET_SIZE, WaveBullet

SWEEP_PERIOD = 2.0  # seconds for a sweeping gun to go from one side to the other and back
BULLET_SIZES = {"heavy": HEAVY_BULLET_SIZE, "pellet": 0.022}  # the others are config.ENEMY_BULLET_SIZE
ACCEL_START = 0.35  # "accel" shots start at this share of their speed...
ACCEL_RATE = 0.9  # ...and speed up by this much per second...
ACCEL_TOP = 1.8  # ...up to this many times their speed
CURVE_TIME = 1.5  # "curve" shots bend this long, then fly straight
LASER_WARNING = 1.0  # seconds of thin harmless beam before a laser fires: time to move away
WARNING_WIDTH = 0.008
PROJECTILES = ("rocket", "missile", "cluster")
ROCKET_START = 0.25  # like the Rocket Truck's rockets: they speed up
BOMB_SPEED = 0.3  # like the Bomber's cluster bombs


@dataclass(frozen=True)
class Gun:
    """How one gun fires. Angles in degrees; 0 is straight down.

    pattern: "aimed" (at the player), "fan" (around straight down), "ring" (all around) or "laser" (beams straight
    down). `count` shots `spread` degrees apart (a ring spreads them evenly), every `interval` seconds, `volley`
    times in a row `gap` seconds apart. Each time it fires, the pattern turns by `turn` degrees (a ring firing fast
    with a turn is a spiral). `sweep`: a fan's middle swings that far left and right. `delay`: the first shot waits
    that much more, so guns take turns.

    `style`: "normal", "sniper" (blue), "heavy" (bigger, orange), "pellet" (small), "wave" (violet, snaking across
    its line of flight), "accel" (cyan, starts slow and speeds up) or "curve" (yellow, its path bends by `curve`
    degrees per second for CURVE_TIME seconds). `projectile`: "rocket", "missile" (homing) or "cluster" (a bomb bursting into a ring)
    launched instead of each shot; `speed` is then unused (they have their own).

    A laser fires one beam per `offsets` (x from the gun's middle), `width` wide, for `duration` seconds, each
    announced by a thin harmless beam LASER_WARNING seconds before; the beams follow the gun as the boss sways.
    """

    pattern: str
    interval: float
    speed: float
    count: int = 1
    spread: float = 15.0
    volley: int = 1
    gap: float = 0.15
    turn: float = 0.0
    sweep: float = 0.0
    delay: float = 0.0
    style: str = "normal"
    curve: float = 0.0
    projectile: str = ""
    width: float = 0.06
    duration: float = 1.0
    offsets: tuple[float, ...] = (0.0,)


@dataclass(eq=False)
class AccelBullet(Bullet):
    """A shot starting slow, speeding up by `rate` per second up to `top_speed`."""

    rate: float = 0.5
    top_speed: float = 1.0

    def move(self, dt: float) -> None:
        speed = math.hypot(self.vx, self.vy)
        if 0 < speed < self.top_speed:
            faster = min(self.top_speed, speed + self.rate * dt) / speed
            self.vx, self.vy = self.vx * faster, self.vy * faster
        super().move(dt)


@dataclass(eq=False)
class CurveBullet(Bullet):
    """A shot whose path bends by `turn_rate` degrees per second (positive: counterclockwise) for `bend_time`
    seconds, then goes straight on (it would fly in circles).
    """

    turn_rate: float = 0.0
    bend_time: float = CURVE_TIME

    def move(self, dt: float) -> None:
        bending = min(dt, max(self.bend_time, 0.0))
        self.bend_time -= dt
        angle = math.radians(self.turn_rate * bending)
        cos, sin = math.cos(angle), math.sin(angle)
        self.vx, self.vy = self.vx * cos - self.vy * sin, self.vx * sin + self.vy * cos
        super().move(dt)


@dataclass(eq=False)
class BossBeam(Bullet):
    """A laser beam (or its harmless warning) from under `source` straight down past the bottom of the screen,
    following it; it goes when its time is up or its source is destroyed.
    """

    source: Entity | None = None
    offset_x: float = 0.0

    def move(self, dt: float) -> None:
        if self.source is not None:
            if not self.source.alive:
                self.alive = False
            top = self.source.y - self.source.height / 2
            self.x = self.source.x + self.offset_x
            self.y, self.height = (top + BEAM_BOTTOM) / 2, max(top - BEAM_BOTTOM, 0.0)
        super().move(dt)


def laser_beams(gun: Gun, source: Entity, warning: bool) -> list[Bullet]:
    """A laser gun's beams from `source`, or their thin harmless warnings."""
    beams: list[Bullet] = []
    for offset in gun.offsets:
        beam = BossBeam(
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
        beam.move(0.0)  # in place under its source
        beams.append(beam)
    return beams


def pattern_shots(gun: Gun, source: Entity, target: Entity, turned: float, age: float) -> list[Entity]:
    """One shot of a gun from `source`: its bullets (or projectiles), all at the same time."""
    if not gun.projectile:
        return list(pattern_bullets(gun, source, target, turned, age))
    shots: list[Entity] = []
    for angle in pattern_angles(gun, source, target, turned, age):
        radians = math.radians(angle)
        dx, dy = math.sin(radians), -math.cos(radians)
        if gun.projectile == "missile":
            shots.append(HomingMissile(x=source.x, y=source.y, heading=math.atan2(dy, dx)))
        elif gun.projectile == "rocket":
            shots.append(Rocket(x=source.x, y=source.y, vx=dx * ROCKET_START, vy=dy * ROCKET_START))
        else:
            shots.append(ClusterBomb(x=source.x, y=source.y, vx=dx * BOMB_SPEED, vy=dy * BOMB_SPEED))
    return shots


def pattern_angles(gun: Gun, source: Entity, target: Entity, turned: float, age: float) -> list[float]:
    """The directions of one shot's bullets, in degrees from straight down."""
    if gun.pattern == "aimed":
        middle = math.degrees(math.atan2(target.x - source.x, source.y - target.y))
    else:
        middle = gun.sweep * math.sin(2 * math.pi * age / SWEEP_PERIOD)
    if gun.pattern == "ring":
        return [middle + turned + index * 360 / gun.count for index in range(gun.count)]
    return [middle + turned + (index - (gun.count - 1) / 2) * gun.spread for index in range(gun.count)]


def pattern_bullets(gun: Gun, source: Entity, target: Entity, turned: float, age: float) -> list[Bullet]:
    """One shot of a gun from `source`: its bullets, all at the same time."""
    bullets = []
    for angle in pattern_angles(gun, source, target, turned, age):
        radians = math.radians(angle)
        bullets.append(styled_bullet(gun, source, math.sin(radians) * gun.speed, -math.cos(radians) * gun.speed))
    return bullets


def styled_bullet(gun: Gun, source: Entity, vx: float, vy: float) -> Bullet:
    """A bullet of the gun's style from `source`, flying at (vx, vy) (an "accel" one starts slower)."""
    if gun.style == "wave":
        bullet: Bullet = WaveBullet()
    elif gun.style == "accel":
        bullet = AccelBullet(rate=ACCEL_RATE * gun.speed, top_speed=ACCEL_TOP * gun.speed)
        vx, vy = vx * ACCEL_START, vy * ACCEL_START
    elif gun.style == "curve":
        bullet = CurveBullet(turn_rate=gun.curve)
    else:
        bullet = Bullet()
    bullet.x, bullet.y, bullet.vx, bullet.vy = source.x, source.y, vx, vy
    bullet.width = bullet.height = BULLET_SIZES.get(gun.style, config.ENEMY_BULLET_SIZE)
    bullet.damage, bullet.hostile, bullet.style = config.ENEMY_BULLET_DAMAGE, True, gun.style
    return bullet
