"""Enemy types from 02-enemies.md, independent from rendering.

Each enemy moves itself in `update` and returns the bullets or enemies it creates.
"""

import math
import random
from dataclasses import dataclass
from typing import ClassVar

from pewpy import config
from pewpy.entities import Bullet, Entity

TOP = config.PLAY_HEIGHT / 2
HALF_WIDTH = config.PLAY_WIDTH / 2
HIT_FLASH_TIME = 0.05


@dataclass(eq=False)
class Enemy(Entity):
    """Base enemy: flies with its velocity and never shoots. Subclasses add behavior in `behave`."""

    side_entry: ClassVar[bool] = False  # True: enters from the left/right edge instead of the top
    fire_interval: ClassVar[float] = 1.0
    drop_chance: ClassVar[float] = 0.0  # chance to leave a pickup when shot down
    rammable: ClassVar[bool] = True  # False: ramming it hurts the player but doesn't destroy it (bosses)
    leaves_screen: ClassVar[bool] = True  # False: stays in the game even beyond the edges (bosses)

    health: float = 3.0
    points: int = 100
    fire_cooldown: float = 0.0
    flash_time: float = 0.0
    age: float = 0.0

    def update(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.age += dt
        self.flash_time = max(0.0, self.flash_time - dt)
        created = self.behave(dt, target, scroll_speed)
        self.move(dt)
        return created

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        return []

    @property
    def vulnerable(self) -> bool:
        return True

    def hit(self, damage: float) -> None:
        if not self.vulnerable:
            return
        self.health -= damage
        self.flash_time = HIT_FLASH_TIME
        if self.health <= 0:
            self.alive = False

    def on_destroyed(self) -> list["Enemy"]:
        """Enemies created when this one is shot down."""
        return []

    def wreckage(self) -> list["Enemy"]:
        """Enemies destroyed along with this one (a boss's parts), without points."""
        return []

    def explosions(self) -> list[tuple[float, float, float]]:
        """(x, y, size) of each explosion when it blows up."""
        return [(self.x, self.y, max(self.width, self.height))]

    @property
    def kind_name(self) -> str:
        """What it is, for the effects (debris colors): its class name, like "Drone"."""
        return type(self).__name__

    def enter_from_side(self, direction: int) -> None:
        """Set up movement for a side entry; `direction` is 1 when entering from the left, -1 from the right."""

    def appearance(self) -> str:
        """How to draw the enemy right now: "normal", "flash" (white), "hit" (brighter), "shield",
        "armored" (darker) or "hidden"."""
        return "flash" if self.flash_time > 0 else "normal"

    @property
    def on_screen(self) -> bool:
        return self.y < TOP and abs(self.x) < HALF_WIDTH

    def _reloaded(self, dt: float) -> bool:
        """Count down to the next shot; True when it's time to fire (only while on screen)."""
        self.fire_cooldown -= dt
        if self.fire_cooldown <= 0 and self.on_screen:
            self.fire_cooldown = self.fire_interval
            return True
        return False


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


def angled_bullet(source: Entity, degrees_from_down: float, speed: float) -> Bullet:
    angle = math.radians(degrees_from_down)
    return enemy_bullet(source.x, source.y, math.sin(angle) * speed, -math.cos(angle) * speed)


@dataclass(eq=False)
class Drone(Enemy):
    drop_chance: ClassVar[float] = 0.05
    fire_interval: ClassVar[float] = 1.5
    vy: float = -0.3
    health: float = 3.0
    points: int = 100

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        return [aimed_bullet(self, target, 0.6)] if self._reloaded(dt) else []


@dataclass(eq=False)
class Weaver(Enemy):
    drop_chance: ClassVar[float] = 0.05
    vy: float = -0.35
    health: float = 2.0
    points: int = 80
    base_x: float | None = None

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.base_x is None:
            self.base_x = self.x
        self.x = self.base_x + 0.25 * math.sin(2 * math.pi * self.age / 2.0)
        return []


@dataclass(eq=False)
class Diver(Enemy):
    drop_chance: ClassVar[float] = 0.05
    height: float = 0.12
    vy: float = -0.5
    health: float = 2.0
    points: int = 150
    phase: str = "enter"
    wait_time: float = 0.8

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.phase == "enter" and self.y <= 0.5:
            self.phase, self.vy = "wait", 0.0
        elif self.phase == "wait":
            self.wait_time -= dt
            if self.wait_time <= 0:
                dx, dy = target.x - self.x, target.y - self.y
                distance = math.hypot(dx, dy) or 1.0
                self.phase, self.vx, self.vy = "dive", dx / distance * 1.2, dy / distance * 1.2
        return []

    def appearance(self) -> str:
        if self.phase == "wait" and int(self.wait_time * 10) % 2 == 1:
            return "hidden"
        return super().appearance()


@dataclass(eq=False)
class Gunship(Enemy):
    drop_chance: ClassVar[float] = 0.2
    fire_interval: ClassVar[float] = 2.0
    width: float = 0.2
    height: float = 0.14
    vy: float = -0.15
    health: float = 8.0
    points: int = 300

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        return [angled_bullet(self, angle, 0.5) for angle in (-20, 0, 20)]


@dataclass(eq=False)
class Turret(Enemy):
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 2.5
    width: float = 0.12
    height: float = 0.12
    health: float = 6.0
    points: int = 250
    burst_left: int = 0
    burst_timer: float = 0.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.vy = -scroll_speed  # fixed to the ground
        if self._reloaded(dt):
            self.burst_left, self.burst_timer = 3, 0.0
        if self.burst_left == 0:
            return []
        self.burst_timer -= dt
        if self.burst_timer > 0:
            return []
        self.burst_left -= 1
        self.burst_timer = 0.15
        return [aimed_bullet(self, target, 0.7)]


@dataclass(eq=False)
class Swarmer(Enemy):
    side_entry: ClassVar[bool] = True
    turn_rate: ClassVar[float] = 0.9  # radians per second
    speed: ClassVar[float] = 0.6
    width: float = 0.06
    height: float = 0.06
    health: float = 1.0
    points: int = 50
    heading: float = -math.pi / 2  # direction of travel, radians; -pi/2 is straight down

    def enter_from_side(self, direction: int) -> None:
        self.heading = 0.0 if direction > 0 else math.pi

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        # Curve toward straight down, once inside the play area: it enters off screen and flies straight in first,
        # so the curve is the same wherever it came from.
        if abs(self.x) <= HALF_WIDTH + self.width / 2:
            difference = (-math.pi / 2 - self.heading + math.pi) % (2 * math.pi) - math.pi
            self.heading += max(-self.turn_rate * dt, min(self.turn_rate * dt, difference))
        self.vx, self.vy = math.cos(self.heading) * self.speed, math.sin(self.heading) * self.speed
        return []


@dataclass(eq=False)
class Sniper(Enemy):
    drop_chance: ClassVar[float] = 0.15
    fire_interval: ClassVar[float] = 3.0
    charge_duration: ClassVar[float] = 0.5
    stay_duration: ClassVar[float] = 12.0
    width: float = 0.08
    height: float = 0.14
    vy: float = -0.3
    health: float = 5.0
    points: int = 350
    phase: str = "enter"
    stay_time: float = 0.0
    charge_time: float = 0.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.phase == "enter":
            if self.y <= 0.7:
                self.phase, self.vy, self.vx = "stay", 0.0, 0.15 if self.x <= 0 else -0.15
            return []
        if self.phase == "leave":
            return []

        self.stay_time += dt
        if self.stay_time >= self.stay_duration:
            self.phase, self.vx, self.vy, self.charge_time = "leave", 0.0, 0.3, 0.0
            return []
        if abs(self.x) > HALF_WIDTH - self.width / 2 and self.x * self.vx > 0:
            self.vx = -self.vx  # bounce off the screen edge

        if self.charge_time > 0:
            self.charge_time -= dt
            return [aimed_bullet(self, target, 0.9, style="sniper")] if self.charge_time <= 0 else []
        if self._reloaded(dt):
            self.charge_time = self.charge_duration
        return []

    def appearance(self) -> str:
        return "flash" if self.charge_time > 0 else super().appearance()


@dataclass(eq=False)
class Mine(Enemy):
    width: float = 0.06
    height: float = 0.06
    health: float = 1.0
    points: int = 20

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.vx, self.vy = 0.0, -scroll_speed  # fixed to the ground
        return []


@dataclass(eq=False)
class MineLayer(Enemy):
    drop_chance: ClassVar[float] = 0.1
    side_entry: ClassVar[bool] = True
    fire_interval: ClassVar[float] = 1.0
    width: float = 0.18
    height: float = 0.08
    health: float = 4.0
    points: int = 300

    def enter_from_side(self, direction: int) -> None:
        self.vx = 0.35 * direction

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        return [Mine(x=self.x, y=self.y - self.height / 2)] if self._reloaded(dt) else []


@dataclass(eq=False)
class ShieldCarrier(Enemy):
    drop_chance: ClassVar[float] = 0.3
    shield_up_duration: ClassVar[float] = 2.0
    shield_down_duration: ClassVar[float] = 1.5
    width: float = 0.2
    height: float = 0.2
    vy: float = -0.12
    health: float = 10.0
    points: int = 500
    was_shielded: bool = True

    @property
    def shielded(self) -> bool:
        return self.age % (self.shield_up_duration + self.shield_down_duration) < self.shield_up_duration

    @property
    def vulnerable(self) -> bool:
        return not self.shielded

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        shield_dropped = self.was_shielded and not self.shielded
        self.was_shielded = self.shielded
        if shield_dropped and self.on_screen:
            return [angled_bullet(self, angle, 0.45) for angle in range(0, 360, 45)]
        return []

    def appearance(self) -> str:
        return "shield" if self.shielded else super().appearance()


@dataclass(eq=False)
class Splitter(Enemy):
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 2.0
    width: float = 0.14
    height: float = 0.14
    vy: float = -0.25
    health: float = 6.0
    points: int = 200

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        return [aimed_bullet(self, target, 0.5)] if self._reloaded(dt) else []

    def on_destroyed(self) -> list[Enemy]:
        return [Swarmer(x=self.x, y=self.y, heading=math.radians(angle)) for angle in (-135, -90, -45)]


ENEMY_TYPES: dict[str, type[Enemy]] = {
    "drone": Drone,
    "weaver": Weaver,
    "diver": Diver,
    "gunship": Gunship,
    "turret": Turret,
    "swarmer": Swarmer,
    "sniper": Sniper,
    "mine_layer": MineLayer,
    "shield_carrier": ShieldCarrier,
    "splitter": Splitter,
}


def make_enemy(
    kind: str, x: float, y: float, side: str, rng: random.Random, top: float = TOP, edge: float = HALF_WIDTH
) -> Enemy:
    """Create an enemy of `kind` just outside the screen, ready to enter.

    Top entries use `x`; side entries use `side` ("left" or "right") and `y`. `top` and `edge` are where the
    screen really ends above and on the sides (the tilted camera shows more than the play area), so enemies
    appear off screen and fly in.
    """
    enemy = ENEMY_TYPES[kind]()
    if enemy.side_entry:
        direction = 1 if side == "left" else -1
        enemy.x = -direction * (edge + enemy.width / 2)
        enemy.y = y
        enemy.enter_from_side(direction)
    else:
        max_x = HALF_WIDTH - enemy.width / 2
        enemy.x = max(-max_x, min(max_x, x))
        enemy.y = top + enemy.height / 2
    # Stagger the first shot so a group doesn't fire all at once.
    enemy.fire_cooldown = rng.uniform(0.3, enemy.fire_interval)
    return enemy
