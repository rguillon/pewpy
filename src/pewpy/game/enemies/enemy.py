"""The one kind of enemy (02-enemies.md): every enemy, boss, part and projectile is an Enemy.

Each runs its description (EnemySpec, see spec.py). Independent from rendering.

Each frame (`update`) it counts down its state's timer, goes to another state if one of the state's exits says so,
moves (motions/), fires its state's guns (pewpy.game.weapons.guns), then moves with its speed. It returns
the bullets and enemies it created. The ways out are checked by exits/, what's done on the way by actions/: they all
act on its Body (body.py).
"""

from __future__ import annotations  # an enemy's parts are enemies too

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pewpy import config
from pewpy.game.enemies.body import Body
from pewpy.game.enemies.kinds import KINDS
from pewpy.game.enemies.mounts import model_mounts
from pewpy.game.enemies.spec import EnemySpec, Part, State
from pewpy.game.weapons.guns import GunState, Shooter, step

if TYPE_CHECKING:
    from pewpy.game.enemies.actions import Action
    from pewpy.game.enemies.exits import Exit
    from pewpy.game.entities import Entity

HIT_FLASH_TIME = 0.05
WARMUP_FLASH = 0.1  # a boss blinks this fast while its phase warms up


@dataclass(eq=False)
class Enemy(Body):
    """An enemy running its description: its states, guns and parts."""

    spec: EnemySpec = field(default_factory=lambda: EnemySpec(kind=""))
    points: int = 100
    fire_cooldown: float = 0.0  # its first wait before firing (a "staggered" gun), set when it's placed
    flash_time: float = 0.0
    state_index: int = 0
    warmup: float = 0.0  # a phase: seconds left without shooting
    entries: dict[int, int] = field(default_factory=dict)  # how many times it entered each state, by index
    started: bool = False
    timer_override: float | None = None  # replaces its first state's timer (a shell timed to burst on the player)
    parts: list[Enemy] = field(default_factory=list)
    mount: Part | None = None  # a part: its name, and where it is from the core's middle
    core: Enemy | None = field(default=None, repr=False)  # a part: the enemy it belongs to
    parts_released: bool = False

    @classmethod
    def from_spec(cls, spec: EnemySpec, x: float = 0.0, y: float = 0.0) -> Enemy:
        """Make an enemy of `spec` at (x, y), with its parts."""
        enemy = cls(
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
            piece = cls.from_spec(part.spec, x + part.x, y + part.y)
            piece.mount = part
            piece.core = enemy
            enemy.parts.append(piece)
        return enemy

    @classmethod
    def of_kind(
        cls, kind: str, x: float = 0.0, y: float = 0.0, heading: float | None = None, timer: float | None = None
    ) -> Enemy:
        """Make an enemy (or a boss) of the kind named `kind` (see kinds.py) at (x, y).

        It may head another way than its own (radians) or have another first timer (see Enemy.timer_override).
        """
        enemy = cls.from_spec(KINDS[kind], x, y)
        if heading is not None:
            enemy.heading = heading
        enemy.timer_override = timer
        return enemy

    @property
    def part_name(self) -> str:
        """A part: its name ("" for anything else)."""
        return self.mount.name if self.mount else ""

    @property
    def full_health(self) -> float:
        """Its health when it came in."""
        return self.spec.health

    @property
    def half_span(self) -> float:
        """Half the width of the whole enemy, parts included."""
        return self.spec.half_span

    @property
    def visits(self) -> int:
        """How many times it entered its current state."""
        return self.entries[self.state_index]

    def destroyed(self, part: str) -> bool:
        """Tell whether its part `part` is destroyed."""
        return any(piece.part_name == part and not piece.alive for piece in self.parts)

    @property
    def kind(self) -> str:
        """Its kind's name."""
        return self.spec.kind

    @property
    def kind_name(self) -> str:
        """What it is, for the effects (debris colors): its drawing, or its kind."""
        return self.spec.drawing or self.spec.kind

    @property
    def drawing(self) -> str:
        """Its model: models/<group>/<drawing>.json, or a part's in it ("model:part"; "": built in code)."""
        return self.spec.drawing

    @property
    def state(self) -> State:
        """The state it's in."""
        return self.spec.states[self.state_index]

    @property
    def side_entry(self) -> bool:
        """Whether it enters from the left or right edge instead of the top."""
        return self.spec.side_entry

    @property
    def drop_chance(self) -> float:
        """The chance it drops a pickup when destroyed."""
        return self.spec.drop_chance

    @property
    def rammable(self) -> bool:
        """Whether the player can ram it."""
        return self.spec.rammable

    @property
    def ground(self) -> bool:
        """Whether it sits or drives on the ground."""
        return self.spec.ground

    @property
    def leaves_screen(self) -> bool:
        """Whether it goes away beyond the edges (bosses stay)."""
        return self.spec.leaves_screen

    @property
    def is_boss(self) -> bool:
        """Whether it's a boss."""
        return self.spec.boss

    @property
    def facing(self) -> str:
        """How its model turns: "travel", "player", "spin" or "" (see EnemySpec.facing)."""
        return self.state.faces or self.spec.facing

    @property
    def faces_travel(self) -> bool:
        """Whether its model turns the way it travels."""
        return self.facing == "travel"

    @property
    def fire_interval(self) -> float:
        """The interval of its staggered gun: its first shot comes up to that late (see make_enemy)."""
        guns = [gun for state in self.spec.states for _, gun in state.guns if gun.staggered]
        return guns[0].interval if guns else 1.0

    @property
    def vulnerable(self) -> bool:
        """Whether shots hurt it in its current state (it and its parts: not while it's coming to its place)."""
        return self.state.vulnerable and not (self.core or self).arriving

    @property
    def arriving(self) -> bool:
        """Whether it's still coming to its place (see State.coming_in)."""
        return self.state.coming_in

    @property
    def health_fraction(self) -> float:
        """Health left of the enemy and its parts together, from 1 (full) to 0."""
        full = self.spec.health + sum(part.spec.health for part in self.spec.parts)
        left = max(self.health, 0.0) + sum(max(part.health, 0.0) for part in self.parts if part.alive)
        return left / full

    def update(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        """Advance it by `dt` seconds; return the bullets and enemies it created."""
        self.age += dt
        self.flash_time = max(0.0, self.flash_time - dt)
        created = self.behave(dt, target, scroll_speed)
        self.move(dt)
        self._carry_parts()
        if self.parts and not self.parts_released:  # the parts join the world with it
            self.parts_released = True
            created = [*self.parts, *created]
        return created

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        """Run its state: count down, take an exit, do the motions and fire the guns; return what it created."""
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
                motion.apply(self, dt, target, scroll_speed)
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
        self._carry_parts()

    def enter_from_side(self, direction: int) -> None:
        """Set up a side entry; `direction` is 1 when entering from the left, -1 from the right."""
        if self.spec.side_speed:
            self.vx = self.spec.side_speed * config.WIDTH_SCALE * direction  # crosses in the same time on any screen
        self.heading = 0.0 if direction > 0 else math.pi

    def go_to(self, state: str) -> None:
        """Go straight to the state named `state` (its guns ready, its timer full)."""
        self._enter(self.spec.state_index(state))

    def hit(self, damage: float) -> None:
        """Take `damage` (unless it's invulnerable in its state); it dies at no health."""
        if not self.vulnerable:
            return
        self.health -= damage
        self.flash_time = HIT_FLASH_TIME
        if self.health <= 0:
            self.alive = False

    def on_destroyed(self) -> list[Enemy]:
        """Enemies released when this one is shot down."""
        released = []
        for spawn in self.spec.on_destroyed:
            heading = math.radians(spawn.heading) if spawn.heading is not None else None
            released.append(self.of_kind(spawn.kind, self.x, self.y, heading))
        return released

    def wreckage(self) -> list[Enemy]:
        """Enemies destroyed along with this one (its parts left), without points."""
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

    def _carry_parts(self) -> None:
        for mount, part in zip(self.spec.parts, self.parts, strict=True):
            part.x, part.y = self.x + mount.x, self.y + mount.y

    def _tick(self, dt: float) -> None:
        if self.state.timer is not None:
            self.timer -= dt
        self.clock += dt

    def _enter(self, index: int) -> None:
        self.state_index = index
        self.entries[index] = self.entries.get(index, 0) + 1
        state = self.state
        self.timer = state.timer if state.timer is not None else 0.0
        if self.timer_override is not None:
            self.timer, self.timer_override = self.timer_override, None
        self.clock = 0.0
        self.warmup = state.warmup
        self.guns = [GunState(cooldown=self.fire_cooldown if gun.staggered else gun.delay) for _, gun in state.guns]

    def _exit(self, target: Entity, after_guns: bool) -> Exit | None:
        for way_out in self.state.exits:
            if way_out.after_guns == after_guns and way_out.open(self, target):
                return way_out
        return None

    def _go(self, way_out: Exit, target: Entity) -> list[Entity]:
        created = self._do(way_out.then, target)
        self._enter(self.spec.state_index(way_out.to))
        return created

    def _do(self, actions: tuple[Action, ...], target: Entity) -> list[Entity]:
        created: list[Entity] = []
        for action in actions:
            created += action.do(self, target)
        return created

    def _holding(self) -> bool:
        """Whether a gun holds it still: charging, or firing its beam."""
        return any(
            gun.hold and (state.charging > 0 or state.beaming > 0)
            for (_, gun), state in zip(self.state.guns, self.guns, strict=True)
        )

    def _fire(self, dt: float, target: Entity) -> list[Entity]:
        created: list[Entity] = []
        for slot, ((source, gun), state) in enumerate(zip(self.state.guns, self.guns, strict=True)):
            piece = self if not source else next((part for part in self.parts if part.part_name == source), None)
            if piece is not None and piece.alive:
                created += step(gun, state, self.shooter(target, piece, slot), dt)
        return created

    def shooter(self, target: Entity, piece: Enemy | None = None, slot: int = 0) -> Shooter:
        """Return what its guns need to know, firing from `piece` (itself, or one of its parts) at `target`.

        `slot`: which of its state's guns fires (see Gun.weapons).
        """
        piece = self if piece is None else piece
        return Shooter(
            piece,
            target,
            self.age,
            self.clock,
            self.timer,
            piece.on_screen,
            self.of_kind,
            self._stop,
            mounts=piece.mounts(),
            slot=slot,
        )

    def mounts(self) -> dict[int, tuple[float, float]]:
        """Return where its model's weapons fire from, from its middle: turned with its model if it faces its way."""
        mounts = model_mounts(self.spec.drawing)
        if not (self.faces_travel and (self.vx or self.vy)):
            return {number: (mount.x, mount.y) for number, mount in mounts.items()}
        # The model points down the screen; turned to point along its velocity.
        turn = math.atan2(self.vy, self.vx) + math.pi / 2
        cos, sin = math.cos(turn), math.sin(turn)
        return {number: (m.x * cos - m.y * sin, m.x * sin + m.y * cos) for number, m in mounts.items()}

    def _stop(self) -> None:
        self.vx = 0.0
