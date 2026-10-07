"""Where an enemy's guns fire from: the weapons drawn on its model (02-enemies.md, "Enemy weapons").

A model's drawing (`data/models/<group>/<drawing>.json`, or a part's in its model's file, see pewpy.data.read_model)
can list its "weapons" like its "engines": each {"number", "kind", "x", "y"}, `number` naming it (1, 2...: a gun in
the enemy's description picks its weapons by number, see pewpy.game.weapons.guns.Gun.weapons), `kind` what it is
("gun", "cannon", "missile"...: for whoever writes the descriptions, the game doesn't use it), `x` and `y` the column
and row of its barrel's tip (row 0 at the top of the drawing). Its shots come out of the tip's edge facing down the
screen (the way enemies fly).

Only flat ("rows") and 3D ("layers") drawings can have weapons: the game reads their size from the file. Independent
from rendering.
"""

from dataclasses import dataclass
from functools import cache
from typing import Any

from pewpy import config
from pewpy.data import model_path, read_model

WEAPON_KEYS = {"number", "kind", "x", "y"}


@dataclass(frozen=True)
class Mount:
    """A weapon on a model: its number, its kind, and where its shots come out (x, y), from the model's middle."""

    number: int
    kind: str
    x: float
    y: float


@cache
def model_mounts(drawing: str) -> dict[int, Mount]:
    """Return the weapons of a model, by number ({} for none, or for a model built in code: no file)."""
    if not drawing or not model_path(drawing).is_file():
        return {}
    return parse_mounts(*read_model(drawing))


def parse_mounts(data: dict[str, Any], source: str) -> dict[int, Mount]:
    """Read a model file's weapons (ValueError or TypeError, naming `source`, if they're wrong)."""
    entries = data.get("weapons", [])
    if not entries:
        return {}
    if not isinstance(entries, list):
        msg = f"{source}: 'weapons' must be a list"
        raise TypeError(msg)
    columns, rows = _size(data, source)
    voxel = config.MODEL_VOXEL
    mounts: dict[int, Mount] = {}
    for index, entry in enumerate(entries):
        where = f"{source}: weapon {index + 1}"
        if not isinstance(entry, dict) or set(entry) != WEAPON_KEYS:
            msg = f"{where}: expected the keys {sorted(WEAPON_KEYS)}"
            raise ValueError(msg)
        number, kind, x, y = entry["number"], entry["kind"], entry["x"], entry["y"]
        if isinstance(number, bool) or not isinstance(number, int) or number < 1 or number in mounts:
            msg = f"{where}: 'number' must be a whole number, 1 or more, each weapon its own"
            raise ValueError(msg)
        if not isinstance(kind, str) or not kind:
            msg = f"{where}: 'kind' must be a name"
            raise ValueError(msg)
        if not all(isinstance(value, int | float) and not isinstance(value, bool) for value in (x, y)):
            msg = f"{where}: 'x' and 'y' must be numbers"
            raise ValueError(msg)
        if not (0 <= x < columns and 0 <= y < rows):
            msg = f"{where}: ({x}, {y}) is off the model ({columns} x {rows})"
            raise ValueError(msg)
        # From the middle, y up the screen; the shot leaves from the side of the tip's voxel facing down the screen.
        mounts[number] = Mount(number, kind, (x - (columns - 1) / 2) * voxel, ((rows - 1) / 2 - (y + 0.5)) * voxel)
    return mounts


def _size(data: dict[str, Any], source: str) -> tuple[int, int]:
    """Return a drawing's columns and rows."""
    if "layers" in data:
        first = data["layers"][0]
        return len(first[0]), len(first)
    if "rows" in data:
        return len(data["rows"][0]), len(data["rows"])
    msg = f"{source}: only a flat or 3D drawing ('rows' or 'layers') can have weapons"
    raise ValueError(msg)
