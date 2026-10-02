"""Enemy shots (02-enemies.md, "Enemy weapons"): plain, aimed, heavy, snaking shots and laser beams. Independent from
rendering.
"""

import math
from dataclasses import dataclass

from pewpy import config
from pewpy.game.entities import Bullet, Entity

HEAVY_BULLET_SIZE = 0.05  # "heavy" shots: bigger and orange (the hitbox too)
BEAM_BOTTOM = -config.PLAY_HEIGHT / 2 - 0.1  # beams go down past the bottom of the screen


def enemy_bullet(x: float, y: float, vx: float, vy: float, style: str = "normal") -> Bullet:
    return Bullet(
        x=x,
        y=y,
        vx=vx,
        vy=vy,
        width=config.ENEMY_BULLET_SIZE,
        height=config.ENEMY_BULLET_SIZE,
        damage=config.ENEMY_BULLET_DAMAGE,
        hostile=True,
        style=style,
    )


def aimed_bullet(source: Entity, target: Entity, speed: float, style: str = "normal") -> Bullet:
    dx, dy = target.x - source.x, target.y - source.y
    distance = math.hypot(dx, dy) or 1.0
    return enemy_bullet(source.x, source.y, dx / distance * speed, dy / distance * speed, style)


def heavy_bullet(x: float, y: float, vx: float, vy: float) -> Bullet:
    """A big orange shot (see HEAVY_BULLET_SIZE)."""
    bullet = enemy_bullet(x, y, vx, vy, "heavy")
    bullet.width = bullet.height = HEAVY_BULLET_SIZE
    return bullet


def aim_angle(source: Entity, target: Entity) -> float:
    """Degrees from straight down (like `angled_bullet`) of the line from `source` to `target`."""
    return math.degrees(math.atan2(target.x - source.x, source.y - target.y))


def angled_bullet(source: Entity, degrees_from_down: float, speed: float) -> Bullet:
    angle = math.radians(degrees_from_down)
    return enemy_bullet(source.x, source.y, math.sin(angle) * speed, -math.cos(angle) * speed)


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


def wave_shot(x: float, y: float, vx: float, vy: float) -> WaveBullet:
    """A violet shot snaking across its line of flight (like the Serpent's)."""
    size = config.ENEMY_BULLET_SIZE
    return WaveBullet(
        x=x, y=y, vx=vx, vy=vy, width=size, height=size, damage=config.ENEMY_BULLET_DAMAGE, hostile=True, style="wave"
    )


def beam(x: float, top: float, width: float, duration: float) -> Bullet:
    """A laser beam from `top` straight down past the bottom of the screen (like the Lancer's)."""
    shot = enemy_bullet(x, (top + BEAM_BOTTOM) / 2, 0.0, 0.0, "beam")
    shot.width, shot.height, shot.life, shot.pierces = width, top - BEAM_BOTTOM, duration, True
    return shot
