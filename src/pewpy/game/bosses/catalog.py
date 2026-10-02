"""Every boss (02-enemies-bosses.md) by name, loaded from the JSON files in `src/pewpy/bosses/`: the mini bosses,
one halfway through each level (`mini_bosses.json`), and the final bosses, one at the end of each level
(`final_bosses.json`). Placeholders.

Sizes are hitboxes, and have the shape of the boss's drawing in `models/` (the model is drawn at that size with
square voxels). Parts are at (x, y) from the core's middle. A boss's "note" is for the people editing the file.

`mini_bosses.json` gives each boss in full: its parts and its phases, each phase's guns with "from" (the core, or
a part's name) and the fields of a Gun that aren't the defaults. `final_bosses.json` gives only what
final_bosses.final_boss builds a final boss from: its size, difficulty, four attacks and parts.
"""

import json
from typing import Any

from pewpy.data import data_folder
from pewpy.game.bosses.boss import BossSpec, PartSpec, Phase
from pewpy.game.bosses.final_bosses import final_boss
from pewpy.game.weapons.enemy.boss_guns import Gun


def load_mini_bosses() -> dict[str, BossSpec]:
    """The mini bosses of `bosses/mini_bosses.json`, by name, in the file's order."""
    return {name: _mini_boss(boss) for name, boss in _read("mini_bosses.json").items()}


def load_final_bosses() -> dict[str, BossSpec]:
    """The final bosses of `bosses/final_bosses.json`, by name, in the file's order."""
    return {name: _final_boss(boss) for name, boss in _read("final_bosses.json").items()}


def _read(name: str) -> dict[str, dict[str, Any]]:
    return json.loads((data_folder() / "bosses" / name).read_text())


def _mini_boss(data: dict[str, Any]) -> BossSpec:
    return BossSpec(
        **_fields(data, "note", "parts", "phases"),
        parts=tuple(PartSpec(**part) for part in data.get("parts", [])),
        phases=tuple(_phase(phase) for phase in data["phases"]),
    )


def _phase(data: dict[str, Any]) -> Phase:
    return Phase(
        guns=tuple((gun["from"], Gun(**_fields(gun, "from"))) for gun in data["guns"]), **_fields(data, "guns")
    )


def _fields(data: dict[str, Any], *leave_out: str) -> dict[str, Any]:
    """The fields of a spec, but `leave_out`, with lists as tuples (the specs are frozen)."""
    return {
        key: tuple(value) if isinstance(value, list) else value for key, value in data.items() if key not in leave_out
    }


def _final_boss(data: dict[str, Any]) -> BossSpec:
    attacks = data["attacks"]
    return final_boss(
        data["name"],
        data["drawing"],
        data["width"],
        data["height"],
        data["difficulty"],
        (attacks["front"], attacks["back"], attacks["core"], attacks["rage"]),
        tuple((part["drawing"], part["x"], part["y"], part["width"], part["height"]) for part in data["parts"]),
    )


MINI_BOSSES = load_mini_bosses()
FINAL_BOSSES = load_final_bosses()
BOSSES: dict[str, BossSpec] = {**MINI_BOSSES, **FINAL_BOSSES}
