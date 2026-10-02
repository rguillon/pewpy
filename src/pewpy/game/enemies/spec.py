"""What an enemy is and does, as data (02-enemies.md): its body, and the states it goes through, each with its
motions (motions/), its guns, its look and its ways out (exits/). Loaded from the JSON files in `data/enemies/` and
`data/bosses/` (a boss is an enemy with parts and phases, see kinds.py). Independent from rendering.

In the JSON files, guns are written as pewpy.game.weapons.guns.parse_gun reads them; their origins can be shares of
the enemy's size or model cubes (see guns.distance).
"""

from __future__ import annotations  # a boss's parts are enemies too: EnemySpec and Part refer to each other

import json
from dataclasses import dataclass
from typing import Any

from pewpy import config
from pewpy.data import data_folder
from pewpy.game.enemies.actions import Action, parse_action
from pewpy.game.enemies.errors import EnemySpecError
from pewpy.game.enemies.exits import Exit, parse_exit
from pewpy.game.enemies.motions import Motion, parse_motion
from pewpy.game.weapons.guns import Distance, Gun, parse_gun


@dataclass(frozen=True)
class State:
    name: str
    timer: float | None = None  # counts down from this when the state starts (see the exits' Timer)
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
    spec: EnemySpec
    x: float
    y: float


@dataclass(frozen=True)
class EnemySpec:
    kind: str
    name: str = ""  # shown over a boss's health bar
    drawing: str = ""  # its model: models/<drawing>.json ("": built in code, see graphics/models/)
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
    data["motions"] = tuple(parse_motion(motion) for motion in data.get("motions", []))
    data["guns"] = tuple((gun.get("from", ""), parse_gun(gun)) for gun in data.get("guns", []))
    data["exits"] = tuple(parse_exit(exit_) for exit_ in data.get("exits", []))
    return State(**data)
