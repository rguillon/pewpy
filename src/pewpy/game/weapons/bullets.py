"""The kinds of shots that aren't plain bullets (01-gameplay.md, 02-enemies.md "Enemy weapons"): missiles, snaking,
accelerating and curving shots, and laser beams. The guns fire them (see guns.py). Independent from rendering.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

from pewpy import config
from pewpy.game.entities import Bullet, Entity

BEAM_BOTTOM = -config.PLAY_HEIGHT / 2 - 0.1  # beams go down past the bottom of the screen
CURVE_TIME = 1.5  # "curve" shots bend this long, then fly straight


@dataclass(eq=False)
class Missile(Bullet):
    """The player's missile: maybe homing (turning towards the nearest target, at most `turn_rate` radians per
    second), maybe blowing up enemies within `splash_radius` too (`splash_damage` each).
    """

    width: float = 0.03
    height: float = 0.07
    homing: bool = False
    turn_rate: float = 0.0
    splash_damage: float = 0.0
    splash_radius: float = 0.0

    def steer(self, dt: float, targets: Sequence[Entity]) -> None:
        """Turn toward the nearest target, at most `turn_rate`; fly straight if there is none."""
        if not self.homing or not targets:
            return
        target = min(targets, key=lambda entity: math.hypot(entity.x - self.x, entity.y - self.y))
        speed = math.hypot(self.vx, self.vy)
        heading = math.atan2(self.vy, self.vx)
        wanted = math.atan2(target.y - self.y, target.x - self.x)
        difference = (wanted - heading + math.pi) % (2 * math.pi) - math.pi
        heading += max(-self.turn_rate * dt, min(self.turn_rate * dt, difference))
        self.vx, self.vy = math.cos(heading) * speed, math.sin(heading) * speed


@dataclass(eq=False)
class WaveBullet(Bullet):
    """A shot snaking from side to side across its line of flight."""

    amplitude: float = 0.06
    period: float = 0.7  # seconds for a full wave
    age: float = 0.0
    line_x: float | None = None  # where it would be flying straight
    line_y: float = 0.0

    def move(self, dt: float) -> None:
        if self.line_x is None:
            self.line_x, self.line_y = self.x, self.y
        self.age += dt
        self.line_x += self.vx * dt
        self.line_y += self.vy * dt
        speed = math.hypot(self.vx, self.vy) or 1.0
        offset = self.amplitude * math.sin(2 * math.pi * self.age / self.period)
        self.x, self.y = self.line_x - self.vy / speed * offset, self.line_y + self.vx / speed * offset


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


def beam(x: float, top: float, width: float, duration: float) -> Bullet:
    """A laser beam from `top` straight down past the bottom of the screen (like the Lancer's)."""
    return Bullet(
        x=x,
        y=(top + BEAM_BOTTOM) / 2,
        width=width,
        height=top - BEAM_BOTTOM,
        damage=config.ENEMY_BULLET_DAMAGE,
        hostile=True,
        style="beam",
        life=duration,
        pierces=True,
    )
