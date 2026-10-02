"""How enemies move (02-enemies.md): each motion of an enemy's state sets its speed (or its place) every frame;
Enemy.move then moves it. Independent from rendering.
"""

import math
from collections.abc import Callable
from typing import TYPE_CHECKING

from pewpy import config
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion

HALF_WIDTH = config.PLAY_WIDTH / 2


def scroll(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Fixed to the ground (or driving on it, `plus` faster)."""
    if motion.stop_x:
        enemy.vx = 0.0
    enemy.vy = -scroll_speed + motion.plus


def patrol(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Sideways at `speed`, towards the middle first (whenever it's standing still sideways)."""
    if enemy.vx == 0:
        enemy.vx = motion.speed if enemy.x <= 0 else -motion.speed


def bounce(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Turn back at the screen's edges (a boss: its parts too, and kept inside)."""
    if motion.clamp:
        limit = HALF_WIDTH - enemy.spec.half_span
        if abs(enemy.x) >= limit and enemy.x * enemy.vx > 0:
            enemy.vx = -enemy.vx
            enemy.x = math.copysign(limit, enemy.x)
    elif abs(enemy.x) > HALF_WIDTH - enemy.width / 2 and enemy.x * enemy.vx > 0:
        enemy.vx = -enemy.vx


def weave(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Snake from side to side around the column it came down."""
    if enemy.base_x is None:
        enemy.base_x = enemy.x
    amplitude = motion.amplitude * config.WIDTH_SCALE if motion.widen else motion.amplitude
    enemy.x = enemy.base_x + amplitude * math.sin(2 * math.pi * enemy.age / motion.period)


def swoop(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Up and down: vy = amplitude * cos(age * rate)."""
    enemy.vy = motion.amplitude * math.cos(enemy.age * motion.rate)


def circle(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Round in a small circle while coming down."""
    angle = enemy.age * motion.turn
    spin = motion.radius * motion.turn
    enemy.vx, enemy.vy = -spin * math.sin(angle), -motion.descent + spin * math.cos(angle)


def steer(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Turn towards the player (or straight down), at most `rate`, flying at `speed`."""
    rate = motion.rate / config.WIDTH_SCALE if motion.widen else motion.rate
    if not motion.inside or abs(enemy.x) <= HALF_WIDTH + enemy.width / 2:
        if motion.goal == "down":
            difference = (-math.pi / 2 - enemy.heading + math.pi) % (2 * math.pi) - math.pi
        else:
            wanted = math.atan2(target.y - enemy.y, target.x - enemy.x)
            difference = (wanted - enemy.heading + math.pi) % (2 * math.pi) - math.pi
        enemy.heading += max(-rate * dt, min(rate * dt, difference))
    forward(enemy, motion, dt, target, scroll_speed)


def forward(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Straight on the way it's heading, at `speed`."""
    enemy.vx, enemy.vy = math.cos(enemy.heading) * motion.speed, math.sin(enemy.heading) * motion.speed


def accelerate(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Speed up by `rate` per second until `top`."""
    speed = math.hypot(enemy.vx, enemy.vy)
    if 0 < speed < motion.top:
        faster = min(motion.top, speed + motion.rate * dt) / speed
        enemy.vx, enemy.vy = enemy.vx * faster, enemy.vy * faster


def track_x(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Sideways towards the player's column, at `speed`; still once within `dead_zone` of it."""
    gap = target.x - enemy.x
    enemy.vx = math.copysign(motion.speed, gap) if abs(gap) > motion.dead_zone else 0.0


def zigzag(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Sideways at `speed`, first towards the player, turning back every `every` seconds and at the edges."""
    enemy.turn_timer -= dt
    if enemy.vx == 0:
        enemy.vx = motion.speed if target.x > enemy.x else -motion.speed
    bounce(enemy, motion, dt, target, scroll_speed)
    if enemy.turn_timer > 0:
        return
    enemy.turn_timer = motion.every
    enemy.vx = -enemy.vx


def erratic(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """A new sideways drift every `every` seconds: speed * sin(turns * a + x * b)."""
    enemy.turn_timer -= dt
    if enemy.turn_timer <= 0:
        enemy.turn_timer = motion.every
        enemy.turns += 1
        enemy.vx = motion.speed * math.sin(enemy.turns * motion.a + enemy.x * motion.b)


MOTIONS: dict[str, Callable[["Enemy", "Motion", float, Entity, float], None]] = {
    "scroll": scroll,
    "patrol": patrol,
    "bounce": bounce,
    "weave": weave,
    "swoop": swoop,
    "circle": circle,
    "steer": steer,
    "forward": forward,
    "accelerate": accelerate,
    "track_x": track_x,
    "zigzag": zigzag,
    "erratic": erratic,
}
