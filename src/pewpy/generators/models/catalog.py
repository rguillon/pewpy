"""The models the Dev menu's browser shows, by category: the player's ships, the enemies and the bosses.

Each with what it is (its name and description, from the game's data), so a new model can be picked to match it.
"""

import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from pewpy.data import data_folder, model_path, split_model_name
from pewpy.game.enemies.kinds import ENEMY_FILES, FINAL_BOSSES_FILE, MINI_BOSSES_FILE
from pewpy.game.level import load_worlds
from pewpy.graphics.models import BUILT_MODELS

CATEGORIES = {"players": "Players", "enemies": "Enemies", "bosses": "Bosses"}  # their titles
BOSS_FILES = (MINI_BOSSES_FILE, FINAL_BOSSES_FILE)
FINAL_PLANS_FILE = "bosses/final_plans.json"  # what the final bosses are made from (see models.final_bosses)


@dataclass(frozen=True)
class BossPart:
    """A boss's part, as its boss's file has it: its name, its drawing, where it is from the core's middle."""

    name: str
    drawing: str
    x: float
    y: float


@dataclass(frozen=True)
class Entry:
    """A model on show: what it is (`key` in its `file`, in data/), its title and description, and its drawing."""

    category: str
    key: str
    file: str
    title: str
    description: str
    drawing: str
    parts: tuple[BossPart, ...] = ()  # its destroyable parts (a boss's, an enemy's)


def read_data(name: str) -> dict:
    """Read a JSON file of data/, like "enemies/catalog.json"."""
    return json.loads((data_folder() / name).read_text())


def entries(category: str) -> list[Entry]:
    """Return the models of a category (see CATEGORIES): in the order of the game's files; the bosses as they're played.

    The bosses: the mini boss of level 1-1, its final boss, the mini boss of 1-2...
    """
    if category == "players":
        return [
            Entry(category, key, "ships.json", ship["name"].title(), ship["description"], ship["drawing"])
            for key, ship in read_data("ships.json").items()
        ]
    if category == "enemies":
        found: dict[str, Entry] = {}  # by drawing: two kinds can share one
        for name in ENEMY_FILES:
            for kind, body in read_data(name).items():
                drawing = body.get("drawing", "")
                if drawing and drawing not in BUILT_MODELS and drawing not in found and _drawn(drawing):
                    note = body.get("note", "")
                    found[drawing] = Entry(category, kind, name, _title(kind), note, drawing, _parts(body))
        return list(found.values())
    bosses = [
        Entry(category, kind, name, body["name"].title(), _boss_description(body), body["drawing"], _parts(body))
        for name in BOSS_FILES
        for kind, body in read_data(name).items()
    ]
    return sorted(bosses, key=_boss_order())


def _boss_order() -> Callable[[Entry], tuple[float, int]]:
    """Order the bosses as they're played: each level's mini boss, then its final boss; any boss in no level last."""
    places: dict[str, float] = {}
    levels = [level for world in load_worlds() for level in world.levels]
    for index, level in enumerate(levels):
        for wave in level.waves:
            places.setdefault(wave.enemy, index)
    return lambda entry: (places.get(entry.key, math.inf), BOSS_FILES.index(entry.file))


def _drawn(drawing: str) -> bool:
    return Path(str(model_path(drawing))).is_file()


def _title(kind: str) -> str:
    return kind.replace("_", " ").title()  # mine_layer: "Mine Layer"


def _parts(body: dict) -> tuple[BossPart, ...]:
    return tuple(BossPart(part["name"], part["drawing"], part["x"], part["y"]) for part in body.get("parts", []))


def _boss_description(body: dict) -> str:
    """Its note, and its parts: how many of each drawing."""
    counts: dict[str, int] = {}
    for part in body.get("parts", []):
        counts[part["drawing"]] = counts.get(part["drawing"], 0) + 1
    parts = ", ".join(f"{count} {split_model_name(drawing)[1]}" for drawing, count in counts.items())
    return " ".join(filter(None, [body.get("note", ""), f"Parts: {parts}." if parts else ""]))
