"""The one kind of enemy (02-enemies.md): every enemy, boss, boss part and projectile is an Enemy running its
description (EnemySpec, see spec.py). Independent from rendering.

Each frame (`update`) it counts down its state's timer, goes to another state if one of the state's exits says so,
moves (motions.py), fires its state's guns (pewpy.game.weapons.guns), then moves with its speed. It returns
the bullets and enemies it created.
"""

import math
from dataclasses import dataclass, field

from pewpy import config
from pewpy.game.enemies.kinds import KINDS
from pewpy.game.enemies.motions import MOTIONS
from pewpy.game.enemies.spec import Action, EnemySpec, Exit, State
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import GunState, Shooter, fire, step

TOP = config.PLAY_HEIGHT / 2
HALF_WIDTH = config.PLAY_WIDTH / 2
BOTTOM = -config.PLAY_HEIGHT / 2
HIT_FLASH_TIME = 0.05
WARMUP_FLASH = 0.1  # a boss blinks this fast while its phase warms up


@dataclass(eq=False)
class Enemy(Entity):
    spec: EnemySpec = field(default_factory=lambda: EnemySpec(kind=""))
    health: float = 3.0
    points: int = 100
    fire_cooldown: float = 0.0  # its first wait before firing (a "staggered" gun), set when it's placed
    flash_time: float = 0.0
    age: float = 0.0
    heading: float = -math.pi / 2  # radians, the way a steering enemy flies
    state_index: int = 0
    timer: float = 0.0  # the state's countdown (see State.timer)
    clock: float = 0.0  # seconds in the state
    warmup: float = 0.0  # a boss's phase: seconds left without shooting
    visits: dict[int, int] = field(default_factory=dict)
    guns: list[GunState] = field(default_factory=list)
    started: bool = False
    timer_override: float | None = None  # replaces its first state's timer (a shell timed to burst on the player)
    base_x: float | None = None  # weave
    turn_timer: float = 0.0  # zigzag, erratic
    turns: int = 0  # erratic
    parts: list["Enemy"] = field(default_factory=list)
    part_name: str = ""  # a boss's part: its name...
    offset_x: float = 0.0  # ...and where it is from the core's middle
    offset_y: float = 0.0
    parts_released: bool = False

    @property
    def kind(self) -> str:
        return self.spec.kind

    @property
    def kind_name(self) -> str:
        """What it is, for the effects (debris colors): its drawing, or its kind."""
        return self.spec.drawing or self.spec.kind

    @property
    def drawing(self) -> str:
        return self.spec.drawing

    @property
    def state(self) -> State:
        return self.spec.states[self.state_index]

    @property
    def side_entry(self) -> bool:
        return self.spec.side_entry

    @property
    def drop_chance(self) -> float:
        return self.spec.drop_chance

    @property
    def rammable(self) -> bool:
        return self.spec.rammable

    @property
    def ground(self) -> bool:
        return self.spec.ground

    @property
    def leaves_screen(self) -> bool:
        return self.spec.leaves_screen

    @property
    def is_boss(self) -> bool:
        return self.spec.boss

    @property
    def facing(self) -> str:
        """How its model turns: "travel", "player", "spin" or "" (see EnemySpec.facing)."""
        return self.state.faces or self.spec.facing

    @property
    def faces_travel(self) -> bool:
        return self.facing == "travel"

    @property
    def fire_interval(self) -> float:
        """The interval of its staggered gun: its first shot comes up to that late (see make_enemy)."""
        guns = [gun for state in self.spec.states for _, gun in state.guns if gun.staggered]
        return guns[0].interval if guns else 1.0

    @property
    def vulnerable(self) -> bool:
        return self.state.vulnerable

    @property
    def on_screen(self) -> bool:
        return self.y < TOP and abs(self.x) < HALF_WIDTH

    @property
    def health_fraction(self) -> float:
        """Health left of the enemy and its parts together, from 1 (full) to 0."""
        full = self.spec.health + sum(part.spec.health for part in self.spec.parts)
        left = max(self.health, 0.0) + sum(max(part.health, 0.0) for part in self.parts if part.alive)
        return left / full

    def update(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.age += dt
        self.flash_time = max(0.0, self.flash_time - dt)
        created = self.behave(dt, target, scroll_speed)
        self.move(dt)
        for part in self.parts:
            part.x, part.y = self.x + part.offset_x, self.y + part.offset_y
        if self.parts and not self.parts_released:  # the parts join the world with it
            self.parts_released = True
            created = [*self.parts, *created]
        return created

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        created: list[Entity] = []
        if not self.started:
            self.started = True
            created += self._do(self.spec.start, target)
            self._enter(0)
        self._tick(dt)
        way_out = self._exit(target, after_guns=False)
        while way_out is not None:
            created += self._go(way_out, target)
            if not way_out.go_on:
                return created
            way_out = self._exit(target, after_guns=False) if way_out.recheck else None
        if not self._holding():
            for motion in self.state.motions:
                MOTIONS[motion.type](self, motion, dt, target, scroll_speed)
        if self.warmup > 0:
            self.warmup -= dt
            return created
        created += self._fire(dt, target)
        way_out = self._exit(target, after_guns=True)
        if way_out is not None:
            created += self._go(way_out, target)
        return created

    def place(self, x: float, y: float) -> None:
        """Put it (and its parts) at (x, y)."""
        self.x, self.y = x, y
        for part in self.parts:
            part.x, part.y = x + part.offset_x, y + part.offset_y

    def enter_from_side(self, direction: int) -> None:
        """Set up a side entry; `direction` is 1 when entering from the left, -1 from the right."""
        if self.spec.side_speed:
            self.vx = self.spec.side_speed * config.WIDTH_SCALE * direction  # crosses in the same time on any screen
        self.heading = 0.0 if direction > 0 else math.pi

    def go_to(self, state: str) -> None:
        """Go straight to the state named `state` (its guns ready, its timer full)."""
        self._enter(self.spec.state_index(state))

    def hit(self, damage: float) -> None:
        if not self.vulnerable:
            return
        self.health -= damage
        self.flash_time = HIT_FLASH_TIME
        if self.health <= 0:
            self.alive = False

    def on_destroyed(self) -> list["Enemy"]:
        """Enemies released when this one is shot down."""
        released = []
        for spawn in self.spec.on_destroyed:
            heading = math.radians(spawn.heading) if spawn.heading is not None else None
            released.append(make(spawn.kind, self.x, self.y, heading))
        return released

    def wreckage(self) -> list["Enemy"]:
        """Enemies destroyed along with this one (a boss's parts), without points."""
        return [part for part in self.parts if part.alive]

    def covered(self, x: float) -> bool:
        """Whether a living part is mounted over the column at `x`: there, shots fly over the core up to the part."""
        return any(part.alive and abs(x - part.x) < part.width / 2 for part in self.parts)

    def explosions(self) -> list[tuple[float, float, float]]:
        """(x, y, size) of each explosion when it blows up."""
        size = max(self.width, self.height)
        if not self.spec.explosions:
            return [(self.x, self.y, size)]
        return [
            (self.x + dx * self.width, self.y + dy * self.height, scale * size)
            for dx, dy, scale in self.spec.explosions
        ]

    def appearance(self) -> str:
        """How to draw it right now: "normal", "flash" (white), "hit" (brighter), "shield", "armored" or "hidden"."""
        state = self.state
        if self.warmup > 0:
            return "flash" if int(self.warmup / WARMUP_FLASH) % 2 == 0 else "normal"
        if state.blink and int(self.timer / state.blink) % 2 == state.blink_on:
            return state.look
        if any(gun.charging > 0 for gun in self.guns):
            return "flash"
        hit = self.flash_time > 0
        if self.spec.hit_look == "hit":
            return "hit" if hit else state.look or "normal"
        if state.look and not state.blink:
            return state.look
        return "flash" if hit else "normal"

    def _tick(self, dt: float) -> None:
        if self.state.timer is not None:
            self.timer -= dt
        self.clock += dt

    def _enter(self, index: int) -> None:
        self.state_index = index
        self.visits[index] = self.visits.get(index, 0) + 1
        state = self.state
        self.timer = state.timer if state.timer is not None else 0.0
        if self.timer_override is not None:
            self.timer, self.timer_override = self.timer_override, None
        self.clock = 0.0
        self.warmup = state.warmup
        self.guns = [GunState(cooldown=self.fire_cooldown if gun.staggered else gun.delay) for _, gun in state.guns]

    def _exit(self, target: Entity, after_guns: bool) -> Exit | None:
        for way_out in self.state.exits:
            if (way_out.volleys > 0) == after_guns and self._can_leave(way_out, target):
                return way_out
        return None

    def _can_leave(self, way_out: Exit, target: Entity) -> bool:  # noqa: C901 (one test per condition)
        if way_out.timer and self.timer > 0:
            return False
        if way_out.clock is not None and self.clock < way_out.clock:
            return False
        if way_out.below_y is not None and self.y > way_out.below_y:
            return False
        if way_out.above_y is not None and self.y < way_out.above_y:
            return False
        if way_out.aligned is not None and abs(target.x - self.x) > way_out.aligned:
            return False
        if way_out.cycle is not None:
            period, start, end = way_out.cycle
            if not start <= self.age % period < end:
                return False
        if self.visits[self.state_index] < way_out.visits:
            return False
        destroyed = {part.part_name for part in self.parts if not part.alive}
        if not set(way_out.parts) <= destroyed:
            return False
        if way_out.health_below and self.health >= way_out.health_below * self.spec.health:
            return False
        if way_out.idle and any(gun.busy for gun in self.guns):
            return False
        return sum(gun.volleys for gun in self.guns) >= way_out.volleys

    def _go(self, way_out: Exit, target: Entity) -> list[Entity]:
        created = self._do(way_out.then, target)
        self._enter(self.spec.state_index(way_out.to))
        return created

    def _do(self, actions: tuple[Action, ...], target: Entity) -> list[Entity]:  # noqa: C901 (one branch per action)
        created: list[Entity] = []
        for action in actions:
            if action.type == "velocity":
                self.vx = self.vx if action.vx is None else action.vx
                self.vy = self.vy if action.vy is None else action.vy
            elif action.type == "toward_middle":
                self.vx = action.speed if self.x <= 0 else -action.speed
            elif action.type == "aim":
                dx, dy = target.x - self.x, target.y - self.y
                distance = math.hypot(dx, dy) or 1.0
                self.vx, self.vy = dx / distance * action.speed, dy / distance * action.speed
            elif action.type == "swerve":
                self.vx = max(-action.limit, min(action.limit, (target.x - self.x) * action.gain))
            elif action.type == "sway":
                self.vx = math.copysign(action.speed * config.WIDTH_SCALE, self.vx or 1.0)
            elif action.type == "relocate":  # somewhere else across the screen, a share of it further (wrapping)
                span = HALF_WIDTH - self.width
                self.x = ((self.x / span + 1) / 2 + action.step) % 1.0 * 2 * span - span
                self.y += action.dy
            elif action.type == "to_bottom":
                self.y = BOTTOM - self.height
            elif action.type == "fire" and action.gun is not None:
                if action.gun.off_screen == "fire" or self.on_screen:
                    created += fire(action.gun, self._shooter(self, target))
            elif action.type == "die":
                self.alive = False
        return created

    def _holding(self) -> bool:
        """Whether a gun holds it still: charging, or firing its beam."""
        return any(
            gun.hold and (state.charging > 0 or state.beaming > 0)
            for (_, gun), state in zip(self.state.guns, self.guns, strict=True)
        )

    def _fire(self, dt: float, target: Entity) -> list[Entity]:
        created: list[Entity] = []
        for (source, gun), state in zip(self.state.guns, self.guns, strict=True):
            piece = self if not source else next((part for part in self.parts if part.part_name == source), None)
            if piece is not None and piece.alive:
                created += step(gun, state, self._shooter(piece, target), dt)
        return created

    def _shooter(self, piece: "Enemy", target: Entity) -> Shooter:
        return Shooter(piece, target, self.age, self.clock, self.timer, piece.on_screen, make, self._stop)

    def _stop(self) -> None:
        self.vx = 0.0


def create(spec: EnemySpec, x: float = 0.0, y: float = 0.0) -> Enemy:
    """An enemy of `spec` at (x, y), with its parts."""
    enemy = Enemy(
        x=x,
        y=y,
        vx=spec.velocity[0],
        vy=spec.velocity[1],
        width=spec.width,
        height=spec.height,
        health=spec.health,
        points=spec.points,
        spec=spec,
        heading=math.radians(spec.heading),
    )
    for part in spec.parts:
        piece = create(part.spec, x + part.x, y + part.y)
        piece.part_name, piece.offset_x, piece.offset_y = part.name, part.x, part.y
        enemy.parts.append(piece)
    return enemy


def make(kind: str, x: float = 0.0, y: float = 0.0, heading: float | None = None, timer: float | None = None) -> Enemy:
    """An enemy (or a boss) of the kind named `kind` (see kinds.py) at (x, y), maybe heading another way than its own
    (radians) or with another first timer (see Enemy.timer_override).
    """
    enemy = create(KINDS[kind], x, y)
    if heading is not None:
        enemy.heading = heading
    enemy.timer_override = timer
    return enemy
