"""What an enemy is and does, as data (02-enemies.md): its body, and the states it goes through.

Each state has its motions (motions/), its guns, its look and its ways out (exits/). Loaded from the JSON files in
`data/enemies/` and `data/bosses/` (see kinds.py), every one the same way: any enemy can have destructible parts, and
be written shortly with `phases` instead of `states`; a boss is an enemy with `"boss": true`, which gives it the
bosses' usual fields (see phases.py). Independent from rendering.

In the JSON files, guns are written as pewpy.game.weapons.guns.parse_gun reads them; their origins can be shares of
the enemy's size or model cubes (see guns.distance), or they fire from the weapons drawn on the model (see mounts.py).
"""

from __future__ import annotations  # an enemy's parts are enemies too: EnemySpec and Part refer to each other

import json
from dataclasses import dataclass
from typing import Any

from pewpy import config
from pewpy.data import data_folder
from pewpy.game.enemies.actions import Action, Fire, parse_action
from pewpy.game.enemies.errors import EnemySpecError
from pewpy.game.enemies.exits import Exit, parse_exit
from pewpy.game.enemies.motions import Motion, parse_motion
from pewpy.game.enemies.mounts import model_mounts
from pewpy.game.enemies.phases import expand_phases, preset
from pewpy.game.weapons.guns import PROJECTILES, Distance, Gun, parse_gun


@dataclass(frozen=True)
class State:
    """One of an enemy's states: its timer, motions, guns, look and ways out."""

    name: str
    timer: float | None = None  # counts down from this when the state starts (see the exits' Timer)
    motions: tuple[Motion, ...] = ()
    guns: tuple[tuple[str, Gun], ...] = ()  # (what fires it: "" for the enemy itself, or a part's name; the gun)
    look: str = ""  # "flash", "hidden", "shield" or "armored" ("": its normal look, flashing when hit)
    blink: float = 0.0  # the look blinks: shown when int(timer left / blink) % 2 == blink_on
    blink_on: int = 1
    warmup: float = 0.0  # a phase: seconds without shooting when it starts, blinking (flash)
    vulnerable: bool = True
    coming_in: bool = False  # still coming to its place: neither it nor its parts can be hurt
    faces: str = ""  # overrides the enemy's `facing` in this state
    exits: tuple[Exit, ...] = ()


@dataclass(frozen=True)
class Spawn:
    """An enemy released when this one is shot down (at its middle)."""

    kind: str
    heading: float | None = None  # degrees, counterclockwise from the right


@dataclass(frozen=True)
class Part:
    """A destructible part of an enemy (a boss's, or any's): an enemy of its own, at (x, y) from the core's middle."""

    name: str
    spec: EnemySpec
    x: float
    y: float


@dataclass(frozen=True)
class EnemySpec:
    """A kind of enemy: its body, its states, its parts."""

    kind: str
    name: str = ""  # shown over a boss's health bar
    drawing: str = ""  # its model: models/<group>/<drawing>.json, "<model>:<part>" a part's in it ("": built in code)
    width: float = 0.1
    height: float = 0.1
    health: float = 3.0
    points: int = 100
    drop_chance: float = 0.0  # chance to leave a pickup when shot down
    velocity: tuple[float, float] = (0.0, 0.0)
    heading: float = -90.0  # degrees, counterclockwise from the right (steering enemies fly this way)
    side_entry: bool = False  # enters from the left/right edge instead of the top
    side_speed: float = 0.0  # its speed across when it does (widened with the screen)
    ground: bool = False  # sits or drives on the ground (levels over water or clouds have none)
    rammable: bool = True  # False: ramming it hurts the player but doesn't destroy it (bosses)
    leaves_screen: bool = True  # False: stays in the game even beyond the edges (bosses)
    placeable: bool = True  # the waves can send it (not projectiles, mines, parts; bosses come as boss waves)
    entry_gap: Distance = 0.0  # entering from the top: its highest point starts that far above the screen
    facing: str = ""  # its model turns: "travel" (the way it flies), "player" (its barrel), "spin"
    boss: bool = False  # a boss: a health bar, and the level goes on (or ends) when it's beaten
    hit_look: str = "flash"  # "hit": brighter when hit, over its state's look (bosses: shot all the time)
    explosions: tuple[tuple[float, float, float], ...] = ()  # (x, y, size) as shares of its size; () one in the middle
    start: tuple[Action, ...] = ()  # done on its first frame
    states: tuple[State, ...] = (State("idle"),)
    on_destroyed: tuple[Spawn, ...] = ()
    parts: tuple[Part, ...] = ()

    @property
    def half_span(self) -> float:
        """Half the width of the whole enemy, parts included."""
        return max([self.width / 2] + [abs(part.x) + part.spec.width / 2 for part in self.parts])

    @property
    def top_reach(self) -> float:
        """How far the enemy reaches above its middle, parts included."""
        return max([self.height / 2] + [part.y + part.spec.height / 2 for part in self.parts])

    def released(self) -> set[str]:
        """Return the kinds of enemy it launches (its guns and its parts') or releases (when shot down)."""
        guns = [gun for spec in (self, *(part.spec for part in self.parts)) for gun in spec.guns()]
        guns += [item for gun in guns for item in gun.sequence]
        kinds = {PROJECTILES[gun.projectile][0] if gun.projectile else gun.spawn for gun in guns} - {""}
        return kinds | {spawn.kind for spawn in self.on_destroyed}

    def guns(self) -> list[Gun]:
        """Return its guns: its states', and those its actions fire."""
        actions = [*self.start, *(action for state in self.states for exit_ in state.exits for action in exit_.then)]
        found = [gun for state in self.states for _, gun in state.guns]
        return found + [action.gun for action in actions if isinstance(action, Fire)]

    def state_index(self, name: str) -> int:
        """Return the index of the state called `name`."""
        return next(index for index, state in enumerate(self.states) if state.name == name)


def load_enemy_specs(name: str) -> dict[str, EnemySpec]:
    """Load the enemies of the JSON file `name` (like "enemies/catalog.json"), by kind, in the file's order."""
    data = json.loads((data_folder() / name).read_text())
    return {kind: parse_enemy(kind, body, f"{name}: {kind}") for kind, body in data.items()}


def parse_enemy(kind: str, data: dict[str, Any], source: str) -> EnemySpec:
    """Read an enemy's description (EnemySpecError, naming `source`, if it's wrong).

    Its preset's fields (see phases.py) are filled in unless it gives them.
    """
    usual = preset(data)
    data = usual.body | data
    data.pop("note", None)
    try:
        if "phases" in data:
            data = expand_phases(data)
        if "voxels" in data:
            columns, rows = data.pop("voxels")
            data["width"], data["height"] = columns * config.MODEL_VOXEL, rows * config.MODEL_VOXEL
        elif "size" in data:
            data["width"], data["height"] = data.pop("size")
        if "points" in data:
            data["points"] = _whole(data["points"])
        if "velocity" in data:
            data["velocity"] = tuple(data["velocity"])
        data["start"] = tuple(parse_action(action) for action in data.get("start", []))
        data["states"] = tuple(parse_state(state, usual.gun) for state in data.get("states", [{"name": "idle"}]))
        data["on_destroyed"] = tuple(Spawn(**spawn) for spawn in data.get("on_destroyed", []))
        data["explosions"] = tuple(tuple(explosion) for explosion in data.get("explosions", []))
        data["parts"] = tuple(parse_part(usual.part | part, source) for part in data.get("parts", []))
        spec = EnemySpec(kind=kind, **data)
    except (TypeError, ValueError) as error:
        raise EnemySpecError(source, str(error)) from error
    _check_weapons(spec, source)
    names = {state.name for state in spec.states}
    for state in spec.states:
        for exit_ in state.exits:
            if exit_.to not in names:
                raise EnemySpecError(source, f"state {state.name!r} goes to unknown state {exit_.to!r}")
    return spec


def _check_weapons(spec: EnemySpec, source: str) -> None:
    """Make sure every weapon a gun fires from is on the model of what fires it (itself, or one of its parts)."""
    drawings = {part.name: part.spec.drawing for part in spec.parts}
    fired = [(drawings.get(name, spec.drawing), gun) for state in spec.states for name, gun in state.guns]
    actions = [*spec.start, *(action for state in spec.states for exit_ in state.exits for action in exit_.then)]
    fired += [(spec.drawing, action.gun) for action in actions if isinstance(action, Fire)]
    try:
        for drawing, gun in fired:
            mounts = model_mounts(drawing)
            for number in [*gun.weapons, *(n for item in gun.sequence for n in item.weapons)]:
                if number not in mounts:
                    msg = f"a gun fires from weapon {number}, which model {drawing or '(built in code)'!r} doesn't have"
                    raise EnemySpecError(source, msg)
    except (OSError, TypeError, ValueError) as error:
        raise EnemySpecError(source, str(error)) from error


def _whole(points: object) -> int:
    """Return points as a whole number (110.0 is 110); anything else is a mistake (ValueError)."""
    if isinstance(points, bool) or not isinstance(points, int | float) or points != int(points):
        msg = f"points must be a whole number, not {points!r}"
        raise ValueError(msg)
    return int(points)


def parse_part(data: dict[str, Any], source: str) -> Part:
    """Read a part: its name, where it is from the middle (x, y), and its body, like an enemy's.

    Its kind is its drawing (like "avalanche:a": a part drawn in its enemy's model file).
    """
    body = dict(data)
    name, x, y = body.pop("name"), body.pop("x"), body.pop("y")
    return Part(name, parse_enemy(body.get("drawing", name), body, f"{source}: {name}"), x, y)


def parse_state(data: dict[str, Any], usual_gun: dict[str, Any] | None = None) -> State:
    """Read a state: its motions, guns (`usual_gun`'s fields filled in unless given) and exits."""
    data = dict(data)
    guns = [(usual_gun or {}) | written for gun in data.get("guns", []) for written in _guns(gun)]
    data["motions"] = tuple(parse_motion(motion) for motion in data.get("motions", []))
    data["guns"] = tuple((gun.get("from", ""), parse_gun(gun)) for gun in guns)
    data["exits"] = tuple(parse_exit(exit_) for exit_ in data.get("exits", []))
    return State(**data)


def _guns(gun: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the gun as it is, or once per part when it comes `from` several (a list): each fires it in turn.

    Their first shots are spread over its interval.
    """
    sources = gun.get("from", "")
    if not isinstance(sources, list):
        return [gun]
    delay, step = gun.get("delay", 0.0), gun["interval"] / len(sources)
    return [gun | {"from": source, "delay": delay + step * index} for index, source in enumerate(sources)]
