"""Bosses from 02-enemies.md, independent from rendering.

A boss is a core (the Boss) and parts (BossPart) placed around it, each one an enemy of its own in the world, so
shots, the laser and missiles hit them like any enemy. The core moves and fires every gun: a gun belongs to the
core or to a part, and falls silent when its part is destroyed. The fight goes through phases, each with its own
guns and speed: a phase ends when some parts are destroyed, or when the core's health falls below a fraction.
While a phase is `armored`, shots bounce off the core: its parts must go first.
"""

import math
from dataclasses import dataclass, field
from typing import ClassVar

from pewpy.enemies import HALF_WIDTH, HEAVY_BULLET_SIZE, TOP, Enemy, enemy_bullet
from pewpy.entities import Bullet, Entity

CORE = "core"  # the gun source that is the boss itself
HOLD_Y = 0.55  # where a boss stops coming down (the top of the screen is at 1)
ENTRY_SPEED = 0.25
PHASE_PAUSE = 1.2  # seconds without shooting when a phase starts, while the core flashes
PHASE_FLASH = 0.1  # the core blinks this fast during the pause
SWEEP_PERIOD = 2.0  # seconds for a sweeping gun to go from one side to the other and back
EXPLOSIONS = ((0.0, 0.0, 1.3), (-0.45, 0.25, 0.7), (0.45, -0.2, 0.7), (0.2, 0.4, 0.6), (-0.3, -0.35, 0.6))


@dataclass(frozen=True)
class Gun:
    """How one gun fires. Angles in degrees; 0 is straight down.

    pattern: "aimed" (at the player), "fan" (around straight down) or "ring" (all around). `count` shots
    `spread` degrees apart (a ring spreads them evenly), every `interval` seconds, `volley` times in a row
    `gap` seconds apart. Each time it fires, the pattern turns by `turn` degrees (a ring firing fast with a turn
    is a spiral). `sweep`: a fan's middle swings that far left and right. `delay`: the first shot waits that much
    more, so guns take turns. `style`: "normal", "sniper" (blue) or "heavy" (bigger, orange).
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


@dataclass(frozen=True)
class PartSpec:
    """A destructible part, at (x, y) from the core's middle."""

    name: str
    drawing: str  # its model: models/<drawing>.json
    x: float
    y: float
    width: float
    height: float
    health: float
    points: int


@dataclass(frozen=True)
class Phase:
    """Guns as (source, gun): the source is CORE or a part's name. `sway`: side to side speed.

    It ends once every part in `until_destroyed` is destroyed, or once the core's health is below `until_below`
    (a fraction of its full health); the last phase lasts until the end."""

    guns: tuple[tuple[str, Gun], ...]
    sway: float
    armored: bool = False
    until_destroyed: tuple[str, ...] = ()
    until_below: float = 0.0


@dataclass(frozen=True)
class BossSpec:
    name: str  # shown over its health bar
    drawing: str
    width: float
    height: float
    health: float
    points: int
    phases: tuple[Phase, ...]
    parts: tuple[PartSpec, ...] = ()

    @property
    def half_span(self) -> float:
        """Half the width of the whole boss, parts included."""
        return max([self.width / 2] + [abs(part.x) + part.width / 2 for part in self.parts])

    @property
    def top_reach(self) -> float:
        """How far the boss reaches above its middle, parts included."""
        return max([self.height / 2] + [part.y + part.height / 2 for part in self.parts])


PLACEHOLDER = BossSpec("", "", 0.1, 0.1, 1.0, 0, (Phase(guns=(), sway=0.0),))  # only for Boss()'s default


@dataclass
class GunState:
    cooldown: float
    volley_left: int = 0
    volley_timer: float = 0.0
    turned: float = 0.0


@dataclass(eq=False)
class BossPart(Enemy):
    """A part of a boss: moved by its boss, never leaves the screen on its own, can't be rammed away."""

    drop_chance: ClassVar[float] = 0.3
    rammable: ClassVar[bool] = False
    leaves_screen: ClassVar[bool] = False
    name: str = ""
    drawing: str = ""
    offset_x: float = 0.0
    offset_y: float = 0.0

    @property
    def kind_name(self) -> str:
        return self.drawing

    def appearance(self) -> str:
        return "hit" if self.flash_time > 0 else "normal"  # shot at all the time: white would hide it


@dataclass(eq=False)
class Boss(Enemy):
    drop_chance: ClassVar[float] = 1.0
    rammable: ClassVar[bool] = False
    leaves_screen: ClassVar[bool] = False
    spec: BossSpec = field(default_factory=lambda: PLACEHOLDER)
    parts: list[BossPart] = field(default_factory=list)
    arrived: bool = False
    phase_index: int = 0
    pause: float = 0.0
    guns: list[GunState] = field(default_factory=list)
    parts_released: bool = False

    @property
    def drawing(self) -> str:
        return self.spec.drawing

    @property
    def kind_name(self) -> str:
        return self.spec.drawing

    @property
    def phase(self) -> Phase:
        return self.spec.phases[self.phase_index]

    @property
    def vulnerable(self) -> bool:
        return not self.phase.armored

    @property
    def health_fraction(self) -> float:
        """Health left of the core and its parts together, from 1 (full) to 0."""
        full = self.spec.health + sum(part.health for part in self.spec.parts)
        left = max(self.health, 0.0) + sum(max(part.health, 0.0) for part in self.parts if part.alive)
        return left / full

    def update(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        created = super().update(dt, target, scroll_speed)
        for part in self.parts:
            part.x, part.y = self.x + part.offset_x, self.y + part.offset_y
        if not self.parts_released:  # the parts join the world with the boss
            self.parts_released = True
            created = [*self.parts, *created]
        return created

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        if not self.arrived:
            self.vy = -ENTRY_SPEED
            if self.y > HOLD_Y:
                return []
            self.arrived, self.vy, self.vx = True, 0.0, self.phase.sway
            self._start_phase()
        self._next_phase_if_done()
        self._sway()
        if self.pause > 0:
            self.pause -= dt
            return []
        created: list[Entity] = []
        for (source, gun), state in zip(self.phase.guns, self.guns, strict=True):
            piece = self._piece(source)
            if piece is not None and piece.alive:
                created += self._fire(gun, state, piece, target, dt)
        return created

    def wreckage(self) -> list[Enemy]:
        return [part for part in self.parts if part.alive]

    def explosions(self) -> list[tuple[float, float, float]]:
        size = max(self.width, self.height)
        return [(self.x + dx * self.width, self.y + dy * self.height, scale * size) for dx, dy, scale in EXPLOSIONS]

    def appearance(self) -> str:
        if self.pause > 0 and self.arrived:
            return "flash" if int(self.pause / PHASE_FLASH) % 2 == 0 else "normal"
        if self.flash_time > 0:
            return "hit"
        return "armored" if self.phase.armored else "normal"

    def _start_phase(self) -> None:
        self.pause = PHASE_PAUSE
        self.guns = [GunState(cooldown=gun.delay) for _, gun in self.phase.guns]
        self.vx = math.copysign(self.phase.sway, self.vx or 1.0)

    def _next_phase_if_done(self) -> None:
        if self.phase_index == len(self.spec.phases) - 1:
            return
        phase = self.phase
        destroyed = {part.name for part in self.parts if not part.alive}
        parts_done = bool(phase.until_destroyed) and set(phase.until_destroyed) <= destroyed
        hurt = phase.until_below > 0 and self.health < phase.until_below * self.spec.health
        if parts_done or hurt:
            self.phase_index += 1
            self._start_phase()

    def _sway(self) -> None:
        limit = HALF_WIDTH - self.spec.half_span
        if abs(self.x) >= limit and self.x * self.vx > 0:
            self.vx = -self.vx  # turn back at the edge of the screen
            self.x = math.copysign(limit, self.x)

    def _piece(self, source: str) -> Enemy | None:
        if source == CORE:
            return self
        return next((part for part in self.parts if part.name == source), None)

    def _fire(self, gun: Gun, state: GunState, piece: Enemy, target: Entity, dt: float) -> list[Entity]:
        state.cooldown -= dt
        if state.cooldown <= 0:
            state.cooldown += gun.interval
            state.volley_left, state.volley_timer = gun.volley, 0.0
        if state.volley_left == 0:
            return []
        state.volley_timer -= dt
        if state.volley_timer > 0:
            return []
        state.volley_left -= 1
        state.volley_timer = gun.gap
        bullets = pattern_bullets(gun, piece, target, state.turned, self.age)
        state.turned += gun.turn
        return list(bullets)


def pattern_bullets(gun: Gun, source: Entity, target: Entity, turned: float, age: float) -> list[Bullet]:
    """One shot of a gun from `source`: its bullets, all at the same time."""
    if gun.pattern == "aimed":
        middle = math.degrees(math.atan2(target.x - source.x, source.y - target.y))
    else:
        middle = gun.sweep * math.sin(2 * math.pi * age / SWEEP_PERIOD)
    if gun.pattern == "ring":
        angles = [middle + turned + index * 360 / gun.count for index in range(gun.count)]
    else:
        angles = [middle + turned + (index - (gun.count - 1) / 2) * gun.spread for index in range(gun.count)]
    bullets = []
    for angle in angles:
        radians = math.radians(angle)
        bullet = enemy_bullet(source.x, source.y, math.sin(radians) * gun.speed, -math.cos(radians) * gun.speed)
        bullet.style = gun.style
        if gun.style == "heavy":
            bullet.width = bullet.height = HEAVY_BULLET_SIZE
        bullets.append(bullet)
    return bullets


def make_boss(spec: BossSpec, x: float, top: float = TOP) -> Boss:
    """A boss (see boss_catalog.py) just above the screen (`top`), with its parts, ready to come down."""
    limit = HALF_WIDTH - spec.half_span
    boss = Boss(
        x=max(-limit, min(limit, x)),
        y=top + spec.top_reach + spec.height / 2,
        width=spec.width,
        height=spec.height,
        health=spec.health,
        points=spec.points,
        spec=spec,
    )
    boss.parts = [
        BossPart(
            x=boss.x + part.x,
            y=boss.y + part.y,
            width=part.width,
            height=part.height,
            health=part.health,
            points=part.points,
            name=part.name,
            drawing=part.drawing,
            offset_x=part.x,
            offset_y=part.y,
        )
        for part in spec.parts
    ]
    return boss
