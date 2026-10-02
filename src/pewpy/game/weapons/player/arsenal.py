"""Player weapons from 01-gameplay.md: bullets, laser and missiles, 5 levels each. Independent from rendering."""

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from pewpy.game.entities import Bullet, Entity
from pewpy.game.weapons.player.secondary import SecondaryWeapon

WEAPONS = ("bullets", "laser", "missiles")
LETTERS = {"bullets": "B", "laser": "L", "missiles": "M"}
MAX_LEVEL = 5

# Bullets: angles from straight up (degrees) and damage per bullet, by level; shots per second, by level
BULLET_FIRE_RATE = 10.0  # at level 1
BULLET_SPEED = 2.5
BULLET_WIDTH = 0.02
BULLET_HEIGHT = 0.05
BULLET_PATTERNS = {
    1: ((0,), 1.0),
    2: ((-12, 0, 12), 0.8),
    3: ((-24, -12, 0, 12, 24), 0.8),
    4: ((-24, -12, 0, 12, 24), 1.0),
    5: ((-30, -20, -10, 0, 10, 20, 30), 1.0),
}
BULLET_FIRE_RATES = {1: BULLET_FIRE_RATE, 2: BULLET_FIRE_RATE, 3: BULLET_FIRE_RATE, 4: 12.0, 5: 12.0}


@dataclass(frozen=True)
class LaserStats:
    width: float
    damage_per_second: float
    pierces: bool


LASER_LEVELS = {
    1: LaserStats(width=0.03, damage_per_second=8.0, pierces=False),
    2: LaserStats(width=0.05, damage_per_second=12.0, pierces=False),
    3: LaserStats(width=0.08, damage_per_second=18.0, pierces=True),
    4: LaserStats(width=0.11, damage_per_second=24.0, pierces=True),
    5: LaserStats(width=0.14, damage_per_second=32.0, pierces=True),
}


@dataclass(frozen=True)
class MissileStats:
    per_shot: int
    homing: bool
    damage: float
    speed: float
    splash_damage: float = 0.0
    fire_rate: float = 3.0  # shots per second


MISSILE_FIRE_RATE = 3.0  # at level 1
MISSILE_TURN_RATE = math.radians(180)  # per second
MISSILE_SPLASH_RADIUS = 0.1
MISSILE_SIDE_OFFSET = 0.05
MISSILE_LEVELS = {
    1: MissileStats(per_shot=1, homing=False, damage=2.5, speed=1.6),
    2: MissileStats(per_shot=1, homing=True, damage=2.5, speed=1.6),
    3: MissileStats(per_shot=2, homing=True, damage=3.0, speed=1.8, splash_damage=1.5),
    4: MissileStats(per_shot=2, homing=True, damage=3.5, speed=2.0, splash_damage=2.0, fire_rate=3.5),
    5: MissileStats(per_shot=2, homing=True, damage=4.0, speed=2.2, splash_damage=2.5, fire_rate=4.0),
}


@dataclass(eq=False)
class Missile(Bullet):
    width: float = 0.03
    height: float = 0.07
    homing: bool = False
    splash_damage: float = 0.0

    def steer(self, dt: float, targets: Sequence[Entity]) -> None:
        """Turn toward the nearest target, at most MISSILE_TURN_RATE; fly straight if there is none."""
        if not self.homing or not targets:
            return
        target = min(targets, key=lambda entity: math.hypot(entity.x - self.x, entity.y - self.y))
        speed = math.hypot(self.vx, self.vy)
        heading = math.atan2(self.vy, self.vx)
        wanted = math.atan2(target.y - self.y, target.x - self.x)
        difference = (wanted - heading + math.pi) % (2 * math.pi) - math.pi
        heading += max(-MISSILE_TURN_RATE * dt, min(MISSILE_TURN_RATE * dt, difference))
        self.vx, self.vy = math.cos(heading) * speed, math.sin(heading) * speed


@dataclass(frozen=True)
class Beam:
    """The laser as drawn this frame: from `bottom` to `top`, centered on `x`."""

    x: float
    bottom: float
    top: float
    width: float


@dataclass
class Arsenal:
    """The three weapons the ship carries, their levels, which one is selected, and the secondary weapon if it has
    one (see secondary.py).
    """

    levels: dict[str, int] = field(default_factory=lambda: dict.fromkeys(WEAPONS, 1))
    selected: str = "bullets"
    cooldown: float = 0.0
    next_side: int = 1  # missiles alternate: 1 = right, -1 = left
    secondary: SecondaryWeapon | None = None

    @property
    def level(self) -> int:
        return self.levels[self.selected]

    def switch(self) -> None:
        self.selected = WEAPONS[(WEAPONS.index(self.selected) + 1) % len(WEAPONS)]

    def upgrade(self, weapon: str) -> bool:
        """Raise `weapon` by one level; False if it was already at the maximum."""
        if self.levels[weapon] >= MAX_LEVEL:
            return False
        self.levels[weapon] += 1
        return True

    def laser(self, firing: bool) -> LaserStats | None:
        """The laser's stats while it is selected and firing, else None."""
        return LASER_LEVELS[self.level] if firing and self.selected == "laser" else None

    def fire(self, dt: float, firing: bool, ship: Entity) -> list[Bullet]:
        """Bullets or missiles shot this frame (the laser is handled by the world, it needs the enemies)."""
        self.cooldown -= dt
        if not firing or self.selected == "laser":
            self.cooldown = max(self.cooldown, 0.0)
            return []
        if self.cooldown > 0:
            return []
        nose_y = ship.y + ship.height / 2
        if self.selected == "bullets":
            self.cooldown += 1.0 / BULLET_FIRE_RATES[self.level]
            angles, damage = BULLET_PATTERNS[self.level]
            return [_bullet(ship.x, nose_y, angle, damage) for angle in angles]

        stats = MISSILE_LEVELS[self.level]
        self.cooldown += 1.0 / stats.fire_rate
        sides = (1, -1) if stats.per_shot == 2 else (self.next_side,)
        self.next_side = -self.next_side
        return [
            Missile(
                x=ship.x + side * (ship.width / 2 - MISSILE_SIDE_OFFSET),
                y=ship.y,
                vy=stats.speed,
                damage=stats.damage,
                homing=stats.homing,
                splash_damage=stats.splash_damage,
            )
            for side in sides
        ]


def _bullet(x: float, y: float, degrees_from_up: float, damage: float) -> Bullet:
    angle = math.radians(degrees_from_up)
    return Bullet(
        x=x,
        y=y,
        vx=math.sin(angle) * BULLET_SPEED,
        vy=math.cos(angle) * BULLET_SPEED,
        width=BULLET_WIDTH,
        height=BULLET_HEIGHT,
        damage=damage,
    )
