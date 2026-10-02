"""What an enemy is and does, as data (02-enemies.md): its body, and the states it goes through, each with its
motions, its guns, its look and its ways out. Loaded from the JSON files in `src/pewpy/enemies/` and `src/pewpy/bosses/`
(a boss is an enemy with parts and phases, see kinds.py). Independent from rendering.

In the JSON files, guns are written as pewpy.game.weapons.guns.parse_gun reads them; their origins can be shares of
the enemy's size or model cubes (see guns.distance).
"""

import json
from dataclasses import dataclass
from typing import Any

from pewpy import config
from pewpy.data import data_folder
from pewpy.game.enemies.motions import MOTIONS
from pewpy.game.weapons.guns import Distance, Gun, parse_gun

ACTIONS = frozenset({"velocity", "toward_middle", "aim", "swerve", "sway", "relocate", "to_bottom", "fire", "die"})


class EnemySpecError(Exception):
    def __init__(self, source: str, message: str) -> None:
        super().__init__(f"{source}: {message}")


class UnknownNameError(ValueError):
    def __init__(self, what: str, name: object) -> None:
        super().__init__(f"unknown {what} {name!r}")


@dataclass(frozen=True)
class Motion:
    """How the enemy moves each frame (see motions.py for each `type`)."""

    type: str
    speed: float = 0.0
    plus: float = 0.0  # scroll: added to the scrolling speed
    stop_x: bool = False  # scroll: no sideways speed either
    amplitude: float = 0.0  # weave: how far to each side; swoop: the up and down speed
    period: float = 1.0  # weave
    widen: bool = False  # weave: amplitude widened with the screen; steer: turn rate narrowed with it
    rate: float = 0.0  # swoop: radians per second; steer: turn rate (radians per second); accelerate: per second
    radius: float = 0.0  # circle
    turn: float = 0.0  # circle: radians per second
    descent: float = 0.0  # circle
    goal: str = "target"  # steer: "target" (the player) or "down"
    inside: bool = False  # steer: only once inside the screen
    top: float = 0.0  # accelerate: its top speed
    dead_zone: float = 0.02  # track_x
    every: float = 0.0  # zigzag, erratic: seconds between turns
    a: float = 0.0  # erratic: the new drift is speed * sin(turns * a + x * b)
    b: float = 0.0
    clamp: bool = False  # bounce: a boss's (its parts included, kept inside)


@dataclass(frozen=True)
class Action:
    """Something done once, when the enemy appears or goes from a state to another."""

    type: str
    vx: float | None = None  # velocity: the speeds set (None: unchanged)
    vy: float | None = None
    speed: float = 0.0  # toward_middle, aim, sway
    gain: float = 0.0  # swerve: vx = gain * (player's x - x), at most `limit` either way
    limit: float = 0.0
    step: float = 0.0  # relocate: moves across the screen by this share of it (wrapping round)...
    dy: float = 0.0  # ...and by this up or down
    gun: Gun | None = None  # fire: one shot of it


@dataclass(frozen=True)
class Exit:
    """A way out of a state, to the state named `to`, once all its conditions hold; `then` is done on the way."""

    to: str
    timer: bool = False  # the state's timer has run out
    clock: float | None = None  # this many seconds in the state
    below_y: float | None = None
    above_y: float | None = None
    aligned: float | None = None  # within this of the player's column
    cycle: tuple[float, float, float] | None = None  # (period, start, end): start <= age % period < end
    visits: int = 0  # the state has been entered this many times (this time included)
    parts: tuple[str, ...] = ()  # these parts are destroyed
    health_below: float = 0.0  # health below this share of the full health
    idle: bool = False  # no gun is charging, firing a beam or in the middle of a volley
    volleys: int = 0  # checked after the guns: this many volleys fired in the state
    then: tuple[Action, ...] = ()
    go_on: bool = False  # the frame goes on in the new state (a boss's phases), instead of ending there...
    recheck: bool = False  # ...after checking the new state's exits too (otherwise one change per frame)


@dataclass(frozen=True)
class State:
    name: str
    timer: float | None = None  # counts down from this when the state starts (see Exit.timer)
    motions: tuple[Motion, ...] = ()
    guns: tuple[tuple[str, Gun], ...] = ()  # (what fires it: "" for the enemy itself, or a part's name; the gun)
    look: str = ""  # "flash", "hidden", "shield" or "armored" ("": its normal look, flashing when hit)
    blink: float = 0.0  # the look blinks: shown when int(timer left / blink) % 2 == blink_on
    blink_on: int = 1
    warmup: float = 0.0  # a boss's phase: seconds without shooting when it starts, blinking (flash)
    vulnerable: bool = True
    faces: str = ""  # overrides the enemy's `facing` in this state
    exits: tuple[Exit, ...] = ()


@dataclass(frozen=True)
class Spawn:
    """An enemy released when this one is shot down (at its middle)."""

    kind: str
    heading: float | None = None  # degrees, counterclockwise from the right


@dataclass(frozen=True)
class Part:
    """A part of a boss: an enemy of its own, at (x, y) from the core's middle."""

    name: str
    spec: "EnemySpec"
    x: float
    y: float


@dataclass(frozen=True)
class EnemySpec:
    kind: str
    name: str = ""  # shown over a boss's health bar
    drawing: str = ""  # its model: models/<drawing>.json ("": built in code, see graphics/models.py)
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
    placeable: bool = True  # the levels can place it (not projectiles, mines, parts, bosses)
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

    def state_index(self, name: str) -> int:
        return next(index for index, state in enumerate(self.states) if state.name == name)


def load_enemy_specs(name: str) -> dict[str, EnemySpec]:
    """The enemies of the JSON file `name` (like "enemies/catalog.json"), by kind, in the file's order."""
    data = json.loads((data_folder() / name).read_text())
    return {kind: parse_enemy(kind, body, f"{name}: {kind}") for kind, body in data.items()}


def parse_enemy(kind: str, data: dict[str, Any], source: str) -> EnemySpec:
    data = dict(data)
    data.pop("note", None)
    try:
        if "voxels" in data:
            columns, rows = data.pop("voxels")
            data["width"], data["height"] = columns * config.MODEL_VOXEL, rows * config.MODEL_VOXEL
        elif "size" in data:
            data["width"], data["height"] = data.pop("size")
        if "velocity" in data:
            data["velocity"] = tuple(data["velocity"])
        data["start"] = tuple(parse_action(action) for action in data.get("start", []))
        data["states"] = tuple(parse_state(state) for state in data.get("states", [{"name": "idle"}]))
        data["on_destroyed"] = tuple(Spawn(**spawn) for spawn in data.get("on_destroyed", []))
        data["explosions"] = tuple(tuple(explosion) for explosion in data.get("explosions", []))
        data["parts"] = tuple(parse_part(part, source) for part in data.get("parts", []))
        spec = EnemySpec(kind=kind, **data)
    except (TypeError, ValueError) as error:
        raise EnemySpecError(source, str(error)) from error
    names = {state.name for state in spec.states}
    for state in spec.states:
        for motion in state.motions:
            if motion.type not in MOTIONS:
                raise EnemySpecError(source, str(UnknownNameError("motion", motion.type)))
        for exit_ in state.exits:
            if exit_.to not in names:
                raise EnemySpecError(source, f"state {state.name!r} goes to unknown state {exit_.to!r}")
    return spec


def parse_part(data: dict[str, Any], source: str) -> Part:
    """A part: its name, where it is from the middle (x, y), and its body, like an enemy's (its kind is its
    drawing).
    """
    body = dict(data)
    name, x, y = body.pop("name"), body.pop("x"), body.pop("y")
    return Part(name, parse_enemy(body.get("drawing", name), body, f"{source}: {name}"), x, y)


def parse_state(data: dict[str, Any]) -> State:
    data = dict(data)
    data["motions"] = tuple(Motion(**motion) for motion in data.get("motions", []))
    data["guns"] = tuple((gun.get("from", ""), parse_gun(gun)) for gun in data.get("guns", []))
    data["exits"] = tuple(parse_exit(exit_) for exit_ in data.get("exits", []))
    return State(**data)


def parse_exit(data: dict[str, Any]) -> Exit:
    data = dict(data)
    data["then"] = tuple(parse_action(action) for action in data.get("then", []))
    if "cycle" in data:
        data["cycle"] = tuple(data["cycle"])
    if "parts" in data:
        data["parts"] = tuple(data["parts"])
    return Exit(**data)


def parse_action(data: dict[str, Any]) -> Action:
    data = dict(data)
    if data["type"] not in ACTIONS:
        raise UnknownNameError("action", data["type"])
    if "gun" in data:
        data["gun"] = parse_gun(data["gun"])
    return Action(**data)
