"""The second fleet of enemies (02-enemies.md): the ones picked from the model candidates. Independent from rendering.

Each enemy's drawing is in `models/<drawing>.json`; its hitbox is the drawing's size (cubes of config.MODEL_VOXEL).
Offsets like a gun's place are in cubes from the drawing's middle (x right, y up the screen), times VOXEL.
"""

import math
from dataclasses import dataclass
from typing import ClassVar

from pewpy import config
from pewpy.game.enemies import (
    HALF_WIDTH,
    ClusterBomb,
    Enemy,
    HomingMissile,
    Mine,
    WaveBullet,
    aim_angle,
    aimed_bullet,
    angled_bullet,
    enemy_bullet,
    heavy_bullet,
)
from pewpy.game.entities import Bullet, Entity

VOXEL = config.MODEL_VOXEL
BOTTOM = -config.PLAY_HEIGHT / 2


def _wave_shot(x: float, y: float, vx: float, vy: float) -> WaveBullet:
    """A violet shot snaking across its line of flight (like the Serpent's)."""
    size = config.ENEMY_BULLET_SIZE
    return WaveBullet(
        x=x, y=y, vx=vx, vy=vy, width=size, height=size, damage=config.ENEMY_BULLET_DAMAGE, hostile=True, style="wave"
    )


def _beam(x: float, top: float, width: float, duration: float) -> Bullet:
    """A laser beam from `top` straight down past the bottom of the screen (like the Lancer's)."""
    bottom = BOTTOM - 0.1
    beam = enemy_bullet(x, (top + bottom) / 2, 0.0, 0.0, "beam")
    beam.width, beam.height, beam.life, beam.pierces = width, top - bottom, duration, True
    return beam


def _bounce(enemy: Enemy) -> None:
    """Turn back at the screen's edges."""
    if abs(enemy.x) > HALF_WIDTH - enemy.width / 2 and enemy.x * enemy.vx > 0:
        enemy.vx = -enemy.vx


def _towards(value: float, target: float, speed: float, dead_zone: float = 0.02) -> float:
    """A speed to move `value` towards `target`: `speed` that way, or 0 when close enough."""
    gap = target - value
    return math.copysign(speed, gap) if abs(gap) > dead_zone else 0.0


@dataclass(eq=False)
class FleetEnemy(Enemy):
    drawing: ClassVar[str] = ""  # its model: models/<drawing>.json


@dataclass(eq=False)
class Hoverer(FleetEnemy):
    """Comes down to `stop_y`, stays there `stay_duration` seconds (`hover` moves and shoots), then flies away."""

    stop_y: ClassVar[float] = 0.6
    stay_duration: ClassVar[float] = 12.0
    leave_speed: ClassVar[float] = 0.3  # up the screen; negative: dives down instead
    phase: str = "enter"
    stay_time: float = 0.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.phase == "enter":
            if self.y <= self.stop_y:
                self.phase, self.vy = "stay", 0.0
            return []
        if self.phase == "leave":
            return []
        self.stay_time += dt
        if self.stay_time >= self.stay_duration and self.can_leave():
            self.phase, self.vx, self.vy = "leave", 0.0, self.leave_speed
            return []
        return self.hover(dt, target)

    def can_leave(self) -> bool:
        return True

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        return []


# ---- Small ones.


@dataclass(eq=False)
class Dart(FleetEnemy):
    """Tiny and fast: dives down, then swerves at the player once, partway down."""

    drawing: ClassVar[str] = "dart"
    faces_travel: ClassVar[bool] = True
    drop_chance: ClassVar[float] = 0.03
    swerve_y: ClassVar[float] = 0.35
    width: float = 9 * VOXEL
    height: float = 10 * VOXEL
    vy: float = -0.7
    health: float = 1.5
    points: int = 80
    swerved: bool = False

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self.swerved and self.y <= self.swerve_y:
            self.swerved = True
            self.vx = max(-0.8, min(0.8, (target.x - self.x) * 2.0))
        return []


@dataclass(eq=False)
class Mite(FleetEnemy):
    """Spirals down in a small circle, firing a shot at the player now and then."""

    drawing: ClassVar[str] = "mite"
    drop_chance: ClassVar[float] = 0.03
    fire_interval: ClassVar[float] = 2.0
    descent: ClassVar[float] = 0.2
    radius: ClassVar[float] = 0.12
    turn_speed: ClassVar[float] = 3.0  # radians per second
    width: float = 13 * VOXEL
    height: float = 9 * VOXEL
    health: float = 1.5
    points: int = 90

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        angle = self.age * self.turn_speed
        spin = self.radius * self.turn_speed
        self.vx, self.vy = -spin * math.sin(angle), -self.descent + spin * math.cos(angle)
        return [aimed_bullet(self, target, 0.5)] if self._reloaded(dt) else []


@dataclass(eq=False)
class Tick(FleetEnemy):
    """Sneaks in from the bottom of the screen, flies up, fires once at the player on the way and leaves at the top."""

    drawing: ClassVar[str] = "tick"
    faces_travel: ClassVar[bool] = True
    drop_chance: ClassVar[float] = 0.05
    speed: ClassVar[float] = 0.45
    fire_y: ClassVar[float] = -0.2
    width: float = 11 * VOXEL
    height: float = 6 * VOXEL
    health: float = 1.0
    points: int = 100
    started: bool = False
    fired: bool = False

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self.started:  # placed at the top like the others: move it below the bottom edge
            self.started, self.y, self.vx, self.vy = True, BOTTOM - self.height, 0.0, self.speed
        if not self.fired and self.y >= self.fire_y:
            self.fired = True
            return [aimed_bullet(self, target, 0.55)]
        return []


@dataclass(eq=False)
class Spark(FleetEnemy):
    """A tiny kamikaze: turns towards the player like a homing missile until its fuel runs out."""

    drawing: ClassVar[str] = "spark"
    faces_travel: ClassVar[bool] = True
    turn_rate: ClassVar[float] = math.radians(150)
    speed: ClassVar[float] = 0.55
    width: float = 5 * VOXEL
    height: float = 7 * VOXEL
    health: float = 1.0
    points: int = 30
    heading: float = -math.pi / 2
    fuel: float = 4.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.fuel -= dt
        if self.fuel > 0:
            wanted = math.atan2(target.y - self.y, target.x - self.x)
            difference = (wanted - self.heading + math.pi) % (2 * math.pi) - math.pi
            self.heading += max(-self.turn_rate * dt, min(self.turn_rate * dt, difference))
        self.vx, self.vy = math.cos(self.heading) * self.speed, math.sin(self.heading) * self.speed
        return []


@dataclass(eq=False)
class Imp(FleetEnemy):
    """Fires a cross of 4 shots that turns a little with each volley."""

    drawing: ClassVar[str] = "imp"
    drop_chance: ClassVar[float] = 0.05
    fire_interval: ClassVar[float] = 1.1
    turn: ClassVar[float] = 22.5  # degrees per volley
    width: float = 11 * VOXEL
    height: float = 12 * VOXEL
    vy: float = -0.3
    health: float = 2.5
    points: int = 120
    volleys: int = 0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        offset = self.volleys * self.turn
        self.volleys += 1
        return [angled_bullet(self, offset + 90 * i, 0.45) for i in range(4)]


@dataclass(eq=False)
class Wisp(FleetEnemy):
    """Blinks: shows for a moment (firing once at the player), vanishes (can't be hit) and shows again elsewhere,
    a bit lower. After a few blinks it drops away."""

    drawing: ClassVar[str] = "wisp"
    drop_chance: ClassVar[float] = 0.08
    stop_y: ClassVar[float] = 0.7
    shown_duration: ClassVar[float] = 1.6
    hidden_duration: ClassVar[float] = 0.5
    blinks: ClassVar[int] = 4
    width: float = 11 * VOXEL
    height: float = 9 * VOXEL
    vy: float = -0.4
    health: float = 2.0
    points: int = 150
    phase: str = "enter"
    timer: float = 0.0
    blinked: int = 0
    fired: bool = False

    @property
    def vulnerable(self) -> bool:
        return self.phase != "hidden"

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.phase == "enter":
            if self.y <= self.stop_y:
                self.phase, self.vy, self.timer = "shown", 0.0, self.shown_duration
            return []
        if self.phase == "leave":
            return []
        self.timer -= dt
        if self.phase == "shown":
            if not self.fired and self.timer <= self.shown_duration / 2:
                self.fired = True
                return [aimed_bullet(self, target, 0.55)]
            if self.timer <= 0:
                self.phase, self.timer = "hidden", self.hidden_duration
        elif self.timer <= 0:
            self._reappear()
        return []

    def _reappear(self) -> None:
        self.blinked += 1
        if self.blinked >= self.blinks:
            self.phase, self.vy = "leave", -0.6
            return
        # Somewhere else across the screen (spread out by the golden ratio), a bit lower.
        span = HALF_WIDTH - self.width
        self.x = ((self.x / span + 1) / 2 + 0.618) % 1.0 * 2 * span - span
        self.y -= 0.15
        self.phase, self.timer, self.fired = "shown", self.shown_duration, False

    def appearance(self) -> str:
        return "hidden" if self.phase == "hidden" else super().appearance()


# ---- Fighters.


@dataclass(eq=False)
class Hornet(FleetEnemy):
    """Zigzags down, turning every 0.6 s, and fires at the player at each turn."""

    drawing: ClassVar[str] = "hornet"
    drop_chance: ClassVar[float] = 0.05
    turn_every: ClassVar[float] = 0.6
    side_speed: ClassVar[float] = 0.35
    width: float = 23 * VOXEL
    height: float = 11 * VOXEL
    vy: float = -0.35
    health: float = 3.0
    points: int = 180
    turn_timer: float = 0.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.turn_timer -= dt
        if self.vx == 0:
            self.vx = self.side_speed if target.x > self.x else -self.side_speed
        _bounce(self)
        if self.turn_timer > 0:
            return []
        self.turn_timer = self.turn_every
        self.vx = -self.vx
        return [aimed_bullet(self, target, 0.55)] if self.on_screen else []


@dataclass(eq=False)
class Albatross(FleetEnemy):
    """Glides down slowly in wide weaves, firing fans of 5 shots."""

    drawing: ClassVar[str] = "albatross"
    drop_chance: ClassVar[float] = 0.15
    fire_interval: ClassVar[float] = 2.5
    width: float = 25 * VOXEL
    height: float = 15 * VOXEL
    vy: float = -0.18
    health: float = 6.0
    points: int = 300
    base_x: float | None = None

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.base_x is None:
            self.base_x = self.x
        self.x = self.base_x + 0.3 * config.WIDTH_SCALE * math.sin(2 * math.pi * self.age / 5.0)
        if not self._reloaded(dt):
            return []
        return [angled_bullet(self, angle, 0.45) for angle in (-40, -20, 0, 20, 40)]


@dataclass(eq=False)
class Kestrel(FleetEnemy):
    """Swoops across the screen from a side: down, then back up, firing aimed triples."""

    drawing: ClassVar[str] = "kestrel"
    side_entry: ClassVar[bool] = True
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 1.4
    width: float = 27 * VOXEL
    height: float = 15 * VOXEL
    health: float = 5.0
    points: int = 300

    def enter_from_side(self, direction: int) -> None:
        self.vx = 0.45 * config.WIDTH_SCALE * direction  # crosses the screen in the same time, whatever its width

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.vy = -0.5 * math.cos(self.age * 1.2)  # swoops down, then climbs back
        if not self._reloaded(dt):
            return []
        aim = aim_angle(self, target)
        return [angled_bullet(self, aim + offset, 0.5) for offset in (-12, 0, 12)]


@dataclass(eq=False)
class Javelin(FleetEnemy):
    """Comes down, lines up with the player (glowing: a warning), then dives straight down very fast."""

    drawing: ClassVar[str] = "javelin"
    drop_chance: ClassVar[float] = 0.08
    stop_y: ClassVar[float] = 0.75
    aim_time: ClassVar[float] = 1.5
    dive_speed: ClassVar[float] = 1.4
    width: float = 15 * VOXEL
    height: float = 29 * VOXEL
    vy: float = -0.3
    health: float = 5.0
    points: int = 250
    phase: str = "enter"
    timer: float = 0.0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if self.phase == "enter" and self.y <= self.stop_y:
            self.phase, self.vy, self.timer = "aim", 0.0, self.aim_time
        elif self.phase == "aim":
            self.timer -= dt
            self.vx = _towards(self.x, target.x, 0.5, 0.03)
            if self.timer <= 0 or self.vx == 0:
                self.phase, self.vx, self.vy = "dive", 0.0, -self.dive_speed
        return []

    def appearance(self) -> str:
        return "flash" if self.phase == "aim" else super().appearance()


@dataclass(eq=False)
class Rapier(FleetEnemy):
    """Streaks straight down, firing pairs of shots out to both sides."""

    drawing: ClassVar[str] = "rapier"
    drop_chance: ClassVar[float] = 0.05
    fire_interval: ClassVar[float] = 0.3
    width: float = 15 * VOXEL
    height: float = 30 * VOXEL
    vy: float = -0.9
    health: float = 3.0
    points: int = 250

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        return [enemy_bullet(self.x, self.y, side * 0.55, -0.1) for side in (-1, 1)]


@dataclass(eq=False)
class Stalker(FleetEnemy):
    """Comes down slowly, chasing the player's side, and fires pairs of shots whenever it's lined up."""

    drawing: ClassVar[str] = "stalker"
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 0.6
    chase_speed: ClassVar[float] = 0.3
    guns: ClassVar[float] = 3 * VOXEL  # from the middle, each side
    width: float = 15 * VOXEL
    height: float = 21 * VOXEL
    vy: float = -0.18
    health: float = 4.0
    points: int = 220

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.vx = _towards(self.x, target.x, self.chase_speed)
        self.fire_cooldown -= dt
        if self.fire_cooldown > 0 or not self.on_screen or abs(target.x - self.x) > 0.06:
            return []
        self.fire_cooldown = self.fire_interval
        return [enemy_bullet(self.x + side * self.guns, self.y, 0.0, -0.6) for side in (-1, 1)]


@dataclass(eq=False)
class Scrapper(FleetEnemy):
    """A lopsided junker: drifts jerkily, changing course every half second, and fires from its side turret."""

    drawing: ClassVar[str] = "scrapper"
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 1.3
    turret: ClassVar[tuple[float, float]] = (-4.5 * VOXEL, 0.5 * VOXEL)  # the turret, from the middle
    width: float = 15 * VOXEL
    height: float = 14 * VOXEL
    vy: float = -0.25
    health: float = 4.0
    points: int = 200
    course_timer: float = 0.0
    courses: int = 0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.course_timer -= dt
        if self.course_timer <= 0:
            self.course_timer = 0.5
            self.courses += 1
            self.vx = 0.25 * math.sin(self.courses * 2.4 + self.x * 7)  # a new, erratic sideways drift
        _bounce(self)
        if not self._reloaded(dt):
            return []
        dx, dy = self.turret
        gun = Entity(x=self.x + dx, y=self.y + dy)
        return [aimed_bullet(gun, target, 0.55)]


# ---- Gunships.


@dataclass(eq=False)
class Brawler(FleetEnemy):
    """A lopsided gunboat: drifts from side to side on its way down, firing heavy shots at the player from its one
    big cannon."""

    drawing: ClassVar[str] = "brawler"
    drop_chance: ClassVar[float] = 0.2
    fire_interval: ClassVar[float] = 1.8
    cannon: ClassVar[tuple[float, float]] = (-8.5 * VOXEL, -4.5 * VOXEL)  # its muzzle, from the middle
    width: float = 29 * VOXEL
    height: float = 20 * VOXEL
    vy: float = -0.15
    vx: float = 0.08
    health: float = 9.0
    points: int = 450

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        _bounce(self)
        if not self._reloaded(dt):
            return []
        dx, dy = self.cannon
        muzzle = Entity(x=self.x + dx, y=self.y + dy)
        shot = aimed_bullet(muzzle, target, 0.5)
        return [heavy_bullet(shot.x, shot.y, shot.vx, shot.vy)]


@dataclass(eq=False)
class Manta(FleetEnemy):
    """Crosses the screen from a side, dropping shots straight down from one wingtip, then the other."""

    drawing: ClassVar[str] = "manta"
    side_entry: ClassVar[bool] = True
    drop_chance: ClassVar[float] = 0.2
    fire_interval: ClassVar[float] = 0.35
    width: float = 31 * VOXEL
    height: float = 15 * VOXEL
    health: float = 7.0
    points: int = 400
    shots: int = 0

    def enter_from_side(self, direction: int) -> None:
        self.vx = 0.25 * config.WIDTH_SCALE * direction  # crosses the screen in the same time, whatever its width

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        self.shots += 1
        tip = self.width * 0.45 * (1 if self.shots % 2 else -1)
        return [enemy_bullet(self.x + tip, self.y, 0.0, -0.5)]


@dataclass(eq=False)
class Broadside(FleetEnemy):
    """Crosses the screen from a side, firing wide fans out to both flanks."""

    drawing: ClassVar[str] = "broadside"
    side_entry: ClassVar[bool] = True
    drop_chance: ClassVar[float] = 0.15
    fire_interval: ClassVar[float] = 1.5
    width: float = 23 * VOXEL
    height: float = 13 * VOXEL
    health: float = 7.0
    points: int = 380

    def enter_from_side(self, direction: int) -> None:
        self.vx = 0.22 * config.WIDTH_SCALE * direction  # crosses the screen in the same time, whatever its width

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        return [angled_bullet(self, side * angle, 0.45) for side in (-1, 1) for angle in (25, 45, 65)]


@dataclass(eq=False)
class Catamaran(FleetEnemy):
    """Its two hulls take turns firing snaking shots straight down."""

    drawing: ClassVar[str] = "catamaran"
    drop_chance: ClassVar[float] = 0.15
    fire_interval: ClassVar[float] = 1.2
    hulls: ClassVar[float] = 6 * VOXEL  # from the middle, each side
    width: float = 17 * VOXEL
    height: float = 11 * VOXEL
    vy: float = -0.2
    health: float = 7.0
    points: int = 350
    shots: int = 0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        self.shots += 1
        side = 1 if self.shots % 2 else -1
        return [_wave_shot(self.x + side * self.hulls, self.y - self.height / 2, 0.0, -0.45)]


@dataclass(eq=False)
class Outrider(Hoverer):
    """Stops high up, fires bursts of paired shots straight down from its pods, then dives away."""

    drawing: ClassVar[str] = "outrider"
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 1.5
    stop_y: ClassVar[float] = 0.55
    stay_duration: ClassVar[float] = 5.0
    leave_speed: ClassVar[float] = -0.7
    pods: ClassVar[float] = 6.5 * VOXEL  # from the middle, each side
    pairs: ClassVar[int] = 3
    width: float = 15 * VOXEL
    height: float = 17 * VOXEL
    vy: float = -0.35
    health: float = 4.0
    points: int = 220
    pairs_left: int = 0
    pair_timer: float = 0.0

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        if self._reloaded(dt):
            self.pairs_left, self.pair_timer = self.pairs, 0.0
        if self.pairs_left == 0:
            return []
        self.pair_timer -= dt
        if self.pair_timer > 0:
            return []
        self.pairs_left -= 1
        self.pair_timer = 0.12
        return [enemy_bullet(self.x + side * self.pods, self.y, 0.0, -0.6) for side in (-1, 1)]


@dataclass(eq=False)
class Needle(Hoverer):
    """Hovers near the top, creeping after the player's side, and fires fast streams of shots straight down."""

    drawing: ClassVar[str] = "needle"
    drop_chance: ClassVar[float] = 0.1
    fire_interval: ClassVar[float] = 2.2
    stop_y: ClassVar[float] = 0.7
    stream: ClassVar[int] = 5
    width: float = 17 * VOXEL
    height: float = 13 * VOXEL
    vy: float = -0.3
    health: float = 4.0
    points: int = 250
    stream_left: int = 0
    stream_timer: float = 0.0

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        self.vx = _towards(self.x, target.x, 0.12)
        if self._reloaded(dt):
            self.stream_left, self.stream_timer = self.stream, 0.0
        if self.stream_left == 0:
            return []
        self.stream_timer -= dt
        if self.stream_timer > 0:
            return []
        self.stream_left -= 1
        self.stream_timer = 0.07
        return [enemy_bullet(self.x, self.y - self.height / 2, 0.0, -0.8)]


@dataclass(eq=False)
class Harrier(Hoverer):
    """Hovers, drifting after the player, and fires rapid bursts of 6 shots at them, a little scattered."""

    drawing: ClassVar[str] = "harrier"
    drop_chance: ClassVar[float] = 0.15
    fire_interval: ClassVar[float] = 2.5
    stop_y: ClassVar[float] = 0.6
    stay_duration: ClassVar[float] = 10.0
    burst: ClassVar[int] = 6
    width: float = 25 * VOXEL
    height: float = 15 * VOXEL
    vy: float = -0.3
    health: float = 6.0
    points: int = 350
    burst_left: int = 0
    burst_timer: float = 0.0

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        self.vx = _towards(self.x, target.x, 0.15)
        if self._reloaded(dt):
            self.burst_left, self.burst_timer = self.burst, 0.0
        if self.burst_left == 0:
            return []
        self.burst_timer -= dt
        if self.burst_timer > 0:
            return []
        self.burst_left -= 1
        self.burst_timer = 0.08
        scatter = 8 * math.sin(self.burst_left * 2.1)  # degrees, different for each shot
        return [angled_bullet(self, aim_angle(self, target) + scatter, 0.6)]


@dataclass(eq=False)
class Howitzer(Hoverer):
    """Stays high up, edging sideways, and lobs shells that burst into a ring of shots where the player was."""

    drawing: ClassVar[str] = "howitzer"
    drop_chance: ClassVar[float] = 0.15
    fire_interval: ClassVar[float] = 2.6
    stop_y: ClassVar[float] = 0.75
    shell_speed: ClassVar[float] = 0.5
    width: float = 29 * VOXEL
    height: float = 15 * VOXEL
    vy: float = -0.3
    health: float = 7.0
    points: int = 400

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        if self.vx == 0:
            self.vx = 0.08 if self.x <= 0 else -0.08
        _bounce(self)
        if not self._reloaded(dt):
            return []
        dx, dy = target.x - self.x, target.y - self.y
        distance = math.hypot(dx, dy) or 1.0
        speed = self.shell_speed
        # The fuse is timed so the shell bursts where the player is now.
        shell = ClusterBomb(
            x=self.x, y=self.y, vx=dx / distance * speed, vy=dy / distance * speed, fuse=distance / speed
        )
        return [shell]


# ---- Carriers and heavies.


@dataclass(eq=False)
class Freighter(FleetEnemy):
    """A slow cargo ship laying mines behind it. Always drops a pickup when shot down."""

    drawing: ClassVar[str] = "freighter"
    drop_chance: ClassVar[float] = 1.0
    fire_interval: ClassVar[float] = 1.4
    width: float = 21 * VOXEL
    height: float = 13 * VOXEL
    vy: float = -0.12
    health: float = 10.0
    points: int = 300

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        return [Mine(x=self.x, y=self.y + self.height / 2)] if self._reloaded(dt) else []


@dataclass(eq=False)
class Brood(FleetEnemy):
    """A pod carrier: releases pairs of Sparks from its two pods."""

    drawing: ClassVar[str] = "brood"
    drop_chance: ClassVar[float] = 0.2
    fire_interval: ClassVar[float] = 2.2
    pods: ClassVar[float] = 7 * VOXEL  # from the middle, each side
    width: float = 23 * VOXEL
    height: float = 16 * VOXEL
    vy: float = -0.15
    health: float = 9.0
    points: int = 450

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        return [Spark(x=self.x + side * self.pods, y=self.y) for side in (-1, 1)]


@dataclass(eq=False)
class Rampart(FleetEnemy):
    """Armored: can't be hurt, except while it opens up to fire a wall of shots straight down."""

    drawing: ClassVar[str] = "rampart"
    drop_chance: ClassVar[float] = 0.3
    closed_duration: ClassVar[float] = 3.0
    open_duration: ClassVar[float] = 1.2
    wall: ClassVar[int] = 7
    width: float = 25 * VOXEL
    height: float = 31 * VOXEL
    vy: float = -0.12
    health: float = 12.0
    points: int = 600
    was_open: bool = False

    @property
    def opened(self) -> bool:
        return self.age % (self.closed_duration + self.open_duration) >= self.closed_duration

    @property
    def vulnerable(self) -> bool:
        return self.opened

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        opening = self.opened and not self.was_open
        self.was_open = self.opened
        if not opening or not self.on_screen:
            return []
        left = self.x - self.width * 0.45
        step = self.width * 0.9 / (self.wall - 1)
        return [enemy_bullet(left + i * step, self.y - self.height / 2, 0.0, -0.4) for i in range(self.wall)]

    def appearance(self) -> str:
        return super().appearance() if self.opened else "armored"


@dataclass(eq=False)
class Condor(FleetEnemy):
    """A big slow wing: launches homing missiles from its wingtips, then fires a spread at the player, in turn."""

    drawing: ClassVar[str] = "condor"
    drop_chance: ClassVar[float] = 0.35
    fire_interval: ClassVar[float] = 1.6
    width: float = 35 * VOXEL
    height: float = 19 * VOXEL
    vy: float = -0.1
    health: float = 18.0
    points: int = 900
    volleys: int = 0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        self.volleys += 1
        if self.volleys % 2:
            tip = self.width * 0.42
            return [HomingMissile(x=self.x + side * tip, y=self.y) for side in (-1, 1)]
        aim = aim_angle(self, target)
        return [angled_bullet(self, aim + offset, 0.5) for offset in (-30, -15, 0, 15, 30, -7.5, 7.5)]


@dataclass(eq=False)
class Behemoth(FleetEnemy):
    """A huge, slow carrier: launches Darts from its sides and fires rings of shots, in turn."""

    drawing: ClassVar[str] = "behemoth"
    drop_chance: ClassVar[float] = 0.6
    fire_interval: ClassVar[float] = 1.6
    ring: ClassVar[int] = 12
    width: float = 35 * VOXEL
    height: float = 33 * VOXEL
    vy: float = -0.1
    health: float = 30.0
    points: int = 1500
    volleys: int = 0

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self._reloaded(dt):
            return []
        self.volleys += 1
        if self.volleys % 2:
            side = self.width * 0.3
            return [Dart(x=self.x + s * side, y=self.y - self.height / 4, vx=s * 0.3, vy=-0.5) for s in (-1, 1)]
        turn = 15 * (self.volleys // 2 % 2)  # every other ring turned, so they don't line up
        return [angled_bullet(self, turn + 360 * i / self.ring, 0.4) for i in range(self.ring)]


@dataclass(eq=False)
class Warhawk(Hoverer):
    """A heavy fighter: strafes near the top, alternating a spiral of shots and a triple of heavy shots at the
    player, then leaves."""

    drawing: ClassVar[str] = "warhawk"
    drop_chance: ClassVar[float] = 0.5
    fire_interval: ClassVar[float] = 2.4
    stop_y: ClassVar[float] = 0.55
    stay_duration: ClassVar[float] = 16.0
    spiral: ClassVar[int] = 12
    width: float = 27 * VOXEL
    height: float = 29 * VOXEL
    vy: float = -0.3
    health: float = 20.0
    points: int = 1000
    volleys: int = 0
    spiral_left: int = 0
    spiral_timer: float = 0.0

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        if self.vx == 0:
            self.vx = 0.15 if self.x <= 0 else -0.15
        _bounce(self)
        if self.spiral_left > 0:
            self.spiral_timer -= dt
            if self.spiral_timer > 0:
                return []
            self.spiral_left -= 1
            self.spiral_timer = 0.1
            return [angled_bullet(self, 30 * self.spiral_left, 0.45)]
        if not self._reloaded(dt):
            return []
        self.volleys += 1
        if self.volleys % 2:
            self.spiral_left, self.spiral_timer = self.spiral, 0.0
            return []
        aim = aim_angle(self, target)
        shots = [angled_bullet(self, aim + offset, 0.5) for offset in (-10, 0, 10)]
        return [heavy_bullet(shot.x, shot.y, shot.vx, shot.vy) for shot in shots]

    def can_leave(self) -> bool:
        return self.spiral_left == 0


@dataclass(eq=False)
class Stormcrow(Hoverer):
    """Heavy: stays high up, drifting, and sweeps streams of shots from side to side, with a pause between sweeps."""

    drawing: ClassVar[str] = "stormcrow"
    drop_chance: ClassVar[float] = 0.35
    stop_y: ClassVar[float] = 0.6
    sweep_duration: ClassVar[float] = 1.6
    pause_duration: ClassVar[float] = 1.2
    shot_every: ClassVar[float] = 0.09
    reach: ClassVar[float] = 60.0  # degrees each side of straight down
    width: float = 31 * VOXEL
    height: float = 23 * VOXEL
    vy: float = -0.3
    health: float = 15.0
    points: int = 800
    shot_timer: float = 0.0

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        if self.vx == 0:
            self.vx = 0.06 if self.x <= 0 else -0.06
        _bounce(self)
        cycle = self.sweep_duration + self.pause_duration
        into = self.stay_time % cycle
        if into >= self.sweep_duration:
            return []
        self.shot_timer -= dt
        if self.shot_timer > 0:
            return []
        self.shot_timer = self.shot_every
        share = into / self.sweep_duration
        sweeping_right = int(self.stay_time // cycle) % 2 == 0
        angle = (share * 2 - 1) * self.reach * (1 if sweeping_right else -1)
        return [angled_bullet(self, angle, 0.5)]


@dataclass(eq=False)
class Pincer(Hoverer):
    """Heavy: comes down, creeps after the player's side and fires two laser beams from its prongs, holding still
    (the gap between them is narrower than a ship: get out from under it). Glows while charging."""

    drawing: ClassVar[str] = "pincer"
    drop_chance: ClassVar[float] = 0.45
    fire_interval: ClassVar[float] = 4.0
    stop_y: ClassVar[float] = 0.55
    stay_duration: ClassVar[float] = 16.0
    charge_duration: ClassVar[float] = 0.9
    beam_duration: ClassVar[float] = 0.7
    beam_width: ClassVar[float] = 0.03
    prongs: ClassVar[float] = 10.5 * VOXEL  # from the middle, each side
    width: float = 31 * VOXEL
    height: float = 31 * VOXEL
    vy: float = -0.3
    health: float = 22.0
    points: int = 1100
    charge_time: float = 0.0
    beam_time: float = 0.0

    def hover(self, dt: float, target: Entity) -> list[Entity]:
        if self.beam_time > 0:
            self.beam_time -= dt
            return []
        if self.charge_time > 0:
            self.charge_time -= dt
            if self.charge_time > 0:
                return []
            self.beam_time = self.beam_duration
            bottom = self.y - self.height / 2
            return [_beam(self.x + side * self.prongs, bottom, self.beam_width, self.beam_duration) for side in (-1, 1)]
        self.vx = _towards(self.x, target.x, 0.12)
        if self._reloaded(dt):
            self.charge_time, self.vx = self.charge_duration, 0.0
        return []

    def can_leave(self) -> bool:
        return self.charge_time <= 0 and self.beam_time <= 0

    def appearance(self) -> str:
        return "flash" if self.charge_time > 0 else super().appearance()


# Every one of them, by the name the levels use.
FLEET: dict[str, type[FleetEnemy]] = {
    "albatross": Albatross,
    "dart": Dart,
    "brawler": Brawler,
    "manta": Manta,
    "hornet": Hornet,
    "mite": Mite,
    "outrider": Outrider,
    "condor": Condor,
    "needle": Needle,
    "kestrel": Kestrel,
    "javelin": Javelin,
    "tick": Tick,
    "warhawk": Warhawk,
    "catamaran": Catamaran,
    "harrier": Harrier,
    "behemoth": Behemoth,
    "wisp": Wisp,
    "rampart": Rampart,
    "imp": Imp,
    "howitzer": Howitzer,
    "stalker": Stalker,
    "spark": Spark,
    "broadside": Broadside,
    "rapier": Rapier,
    "freighter": Freighter,
    "scrapper": Scrapper,
    "brood": Brood,
    "stormcrow": Stormcrow,
    "pincer": Pincer,
}
