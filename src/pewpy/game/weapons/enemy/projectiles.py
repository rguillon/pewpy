"""Enemy projectiles (02-enemies.md, "Enemy weapons"): small enemies of their own, so the player can shoot them down.
They hit like ramming (see config.ENEMY_RAM_DAMAGE) and aren't placed by the levels' waves: other enemies launch them.
Independent from rendering.
"""

import math
from dataclasses import dataclass
from typing import ClassVar

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Entity
from pewpy.game.weapons.enemy.shots import angled_bullet


@dataclass(eq=False)
class Rocket(Enemy):
    """A dumb rocket: flies straight, speeding up until it reaches its top speed."""

    acceleration: ClassVar[float] = 1.0
    top_speed: ClassVar[float] = 1.1
    width: float = 0.03
    height: float = 0.07
    vy: float = -0.25
    health: float = 1.0
    points: int = 10

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        speed = math.hypot(self.vx, self.vy)
        if 0 < speed < self.top_speed:
            faster = min(self.top_speed, speed + self.acceleration * dt) / speed
            self.vx, self.vy = self.vx * faster, self.vy * faster
        return []


@dataclass(eq=False)
class HomingMissile(Enemy):
    """Turns towards the player (at most `turn_rate`) until its fuel runs out, then flies straight on."""

    turn_rate: ClassVar[float] = math.radians(100)  # per second
    speed: ClassVar[float] = 0.45
    width: float = 0.04
    height: float = 0.08
    health: float = 2.0
    points: int = 20
    heading: float = -math.pi / 2  # direction of travel, radians; -pi/2 is straight down
    fuel: float = 3.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.fuel -= dt
        if self.fuel > 0:
            wanted = math.atan2(target.y - self.y, target.x - self.x)
            difference = (wanted - self.heading + math.pi) % (2 * math.pi) - math.pi
            self.heading += max(-self.turn_rate * dt, min(self.turn_rate * dt, difference))
        self.vx, self.vy = math.cos(self.heading) * self.speed, math.sin(self.heading) * self.speed
        return []


@dataclass(eq=False)
class ClusterBomb(Enemy):
    """Falls, then bursts into a ring of shots when its fuse runs out (unless it's shot down first)."""

    shards: ClassVar[int] = 8
    shard_speed: ClassVar[float] = 0.4
    width: float = 0.05
    height: float = 0.05
    vy: float = -0.3
    health: float = 1.0
    points: int = 10
    fuse: float = 1.2

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.fuse <= 0:
            return []  # already burst
        self.fuse -= dt
        if self.fuse > 0:
            return []
        self.alive = False
        return [angled_bullet(self, 360 * i / self.shards + 22.5, self.shard_speed) for i in range(self.shards)]
