"""Saving a new model in place of one of the game's (see browser.py), and what goes with it.

A ship's model file is replaced, its "size" the one it was made to, its hitbox following (see `save_ship`). A boss is
replaced whole: its model file, its core's drawing and new parts (as many as its size has, see
pewpy.generators.models.sized.parts_for) with their drawings in it, under "parts", named after their kind
("<boss>:drill", "<boss>:turret2"...). Its description in its file (data/bosses/) follows: its size, its parts
("drill 1", "turret 2"...) and their places and sizes. A final boss's plan (data/bosses/final_plans.json) gets them,
and the boss is made again from it. A mini boss keeps its hand-written phases, the parts they name replaced by the
new ones (see `remap_phases`).
"""

import itertools
import json
import math
from pathlib import Path
from typing import Any

from pewpy import config
from pewpy.data import PART_SEPARATOR, data_folder, model_path, split_model_name
from pewpy.game.enemies.kinds import ENEMIES
from pewpy.generators.compact_json import compact_json
from pewpy.generators.models.catalog import FINAL_BOSSES_FILE, FINAL_PLANS_FILE, BossPart, Entry, read_data
from pewpy.generators.models.final_bosses.plans import plan_boss
from pewpy.generators.models.final_bosses.writing import boss_json
from pewpy.graphics.models import parse_voxels

PAIRED = 0.005  # world units: two parts this close to mirroring each other are a pair
DECIMALS = 3  # of a place or a size in the enemies' and bosses' files
DEFAULT_PART = {"health": 25.0, "points": 400}  # a new part of a mini boss that had none (placeholder)


def lopsided(parts: tuple[BossPart, ...]) -> bool:
    """Tell whether a boss is lopsided: one of its parts is off its middle, not mirrored by another."""
    return any(
        abs(part.x) >= PAIRED and not any(_mirrors(part, other) for other in parts if other is not part)
        for part in parts
    )


def _mirrors(part: BossPart, other: BossPart) -> bool:
    return other.drawing == part.drawing and abs(other.x + part.x) < PAIRED and abs(other.y - part.y) < PAIRED


def write_model(drawing: str, data: dict) -> None:
    """Write a model's file (replacing it)."""
    Path(str(model_path(drawing))).write_text(json.dumps(data, indent=2) + "\n")


def drawn_size(data: dict) -> list[float]:
    """Return the size a drawing's cubes cover, across and up, as the enemies' files write it."""
    rows = data["layers"][0] if "layers" in data else data["rows"]
    return [round(len(rows[0]) * config.MODEL_VOXEL, DECIMALS), round(len(rows) * config.MODEL_VOXEL, DECIMALS)]


def save_ship(entry: Entry, data: dict, old_size: tuple[float, float]) -> None:
    """Write a ship's model (a new one, or the same at a new "size") in place of the entry's.

    Its hitbox is scaled as much as its size changed from `old_size` (a player's ship's "size" in ships.json, an
    enemy's in its file; an enemy sized by its cubes, "voxels", gets the model's).
    """
    write_model(entry.drawing, data)
    across, up = data["size"][0] / old_size[0], data["size"][1] / old_size[1]
    file = read_data(entry.file)
    body = file[entry.key]
    if entry.category == "players":
        body["size"] = round(body["size"] * math.sqrt(across * up), DECIMALS)
        _write_data(entry.file, json.dumps(file, indent=2) + "\n")
        return
    if "voxels" in body:
        voxels = parse_voxels(data)
        body["voxels"] = [voxels.width, voxels.height]
    else:
        spec = ENEMIES[entry.key]
        body["size"] = [round(spec.width * across, DECIMALS), round(spec.height * up, DECIMALS)]
    _write_data(entry.file, compact_json(file))


def new_parts(boss: str, made: dict) -> list[tuple[dict[str, Any], dict]]:
    """Name a new boss's parts (made by models.sized.sized_boss): each with its place, size and drawing.

    Return each part as its boss's file writes it ({"name", "x", "y", "drawing", "size"}) and its drawing's data. The
    parts of a group share a drawing: "<boss>:<kind>", then "<boss>:<kind>2"... for the next group of that kind.
    """
    drawings: dict[int, str] = {}
    kinds_seen: dict[str, int] = {}
    parts = []
    cube = config.MODEL_VOXEL
    for number, ((data, x, up), group, kind) in enumerate(
        zip(made["parts"], made["groups"], made["kinds"], strict=True), start=1
    ):
        label = kind
        if group not in drawings:
            kinds_seen[label] = kinds_seen.get(label, 0) + 1
            drawings[group] = f"{boss}{PART_SEPARATOR}{label}" + (
                str(kinds_seen[label]) if kinds_seen[label] > 1 else ""
            )
        part = {
            "name": f"{label} {number}",
            "x": round(x * cube, DECIMALS),
            "y": round(up * cube, DECIMALS),
            "drawing": drawings[group],
            "size": drawn_size(data),
        }
        parts.append((part, data))
    return parts


def front_to_back(parts: list[dict[str, Any]], count: int) -> list[list[dict[str, Any]]]:
    """Split parts into `count` lots, the front ones (nearest the bottom of the screen) first.

    A group of parts sharing a drawing stays together when there are enough groups for every lot.
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    for part in parts:
        groups.setdefault(part["drawing"], []).append(part)
    units = sorted(groups.values(), key=lambda unit: sum(part["y"] for part in unit) / len(unit))
    if len(units) < count:
        units = [[part] for part in sorted(parts, key=lambda part: part["y"])]
    bounds = [round(index * len(units) / count) for index in range(count + 1)]
    return [[part for unit in units[low:high] for part in unit] for low, high in itertools.pairwise(bounds)]


def remap_phases(body: dict[str, Any], parts: list[dict[str, Any]]) -> None:
    """Give a mini boss new parts, its phases naming them in place of the old ones.

    The phases ending when parts are destroyed get a lot of the new parts each, the front ones to the first (see
    `front_to_back`); a gun fired from old parts is fired from the new parts that took their place (from all of them
    for old parts no phase waited for). Each new part is as strong and worth as much as the old ones of its phase.
    """
    old = {part["name"]: part for part in body.get("parts", [])}
    waiting = [phase for phase in body["phases"] if "parts" in phase.get("until", {})]
    taking: dict[str, list[str]] = {}  # the new parts taking an old one's place
    template = next(iter(old.values()), DEFAULT_PART)
    stats: dict[str, dict[str, Any]] = {}
    for phase, lot in zip(waiting, front_to_back(parts, max(1, len(waiting))), strict=False):
        names = phase["until"]["parts"]
        for name in names:
            taking[name] = [part["name"] for part in lot]
        for part in lot:
            stats[part["name"]] = old.get(names[0], template)
    everyone = [part["name"] for part in parts]

    def renamed(value: str | list[str]) -> list[str]:
        olds = [value] if isinstance(value, str) else value
        return list(dict.fromkeys(name for old_name in olds for name in taking.get(old_name, everyone)))

    for phase in body["phases"]:
        if phase in waiting:
            phase["until"]["parts"] = renamed(phase["until"]["parts"])
        for gun in phase["guns"]:
            if "from" in gun:
                gun["from"] = renamed(gun["from"])
    body["parts"] = [
        {**part, **{key: value for key, value in stats.get(part["name"], template).items() if key in DEFAULT_PART}}
        for part in parts
    ]


def save_boss(entry: Entry, made: dict) -> None:
    """Write a new boss (made by models.sized.sized_boss) in place of the entry's, its parts new too."""
    parts = new_parts(entry.drawing, made)
    drawings = {split_model_name(part["drawing"])[1]: {**data, "size": part["size"]} for part, data in parts}
    write_model(entry.drawing, {**made["core"], "parts": drawings})
    size = drawn_size(made["core"])
    bosses = read_data(entry.file)
    body = bosses[entry.key]
    body["size"] = size
    if entry.file == FINAL_BOSSES_FILE:
        plans = read_data(FINAL_PLANS_FILE)
        plan = plans[entry.key]
        plan["width"], plan["height"] = size
        plan["parts"] = [
            {
                "drawing": part["drawing"],
                "x": part["x"],
                "y": part["y"],
                "width": part["size"][0],
                "height": part["size"][1],
            }
            for part, _ in parts
        ]
        _write_data(FINAL_PLANS_FILE, json.dumps(plans, indent=2) + "\n")
        bosses[entry.key] = boss_json(plan_boss(plan), plan.get("note", ""))
    else:
        remap_phases(body, [part for part, _ in parts])
    _write_data(entry.file, compact_json(bosses))


def _write_data(name: str, text: str) -> None:
    Path(str(data_folder() / name)).write_text(text)
