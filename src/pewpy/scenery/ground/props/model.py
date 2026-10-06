"""A prop read from data/models/props/<name>.json: fixed parts, with their colors, built once and stretched to each lot.

A description holds the prop's `kind` (what the grounds ask for: "barn", "tank"...), its `size` [width, length,
height]: the box it was drawn in, around (0, 0) with z from 0 at its base, and its `parts`. A part is one shape of
PropMesh (see SHAPES) with its geometry as a list (the method's arguments before the colors, in order), and its
other arguments by name: its colors as [red, green, blue] (`color`, `top`, `cap`, `walls`, `roof`), its `material`
(a name of MATERIALS, PLAIN if left out), and the shape's own options (`segments`, `rings`, `lower`...):

    {"box": [x0, x1, y0, y1, z0, z1], "color": [0.2, 0.2, 0.25], "material": "OFFICE", "top": [0.3, 0.3, 0.3]}

No randomness: a kind with variants is several files of the same kind; each prop picks one by its seed. A prop is
stretched to its lot (its width, length and height), turned a quarter first if its longer side lies the other way.

Independent from Panda3D.
"""

import json
from functools import cache
from typing import Any

import numpy as np

from pewpy.data import data_folder
from pewpy.scenery.ground.props.mesh import (
    FOLIAGE,
    FURNACE,
    HOMES,
    LIGHT,
    METAL,
    OFFICE,
    PLAIN,
    ROOFING,
    PropMesh,
)
from pewpy.scenery.ground.settlement import Prop

PROPS_FOLDER = "models/props"  # in data/
SHAPES = ("box", "cylinder", "disc", "ellipsoid", "gabled", "ridge_roof", "face", "quad", "lathe")
COLORS = ("color", "top", "cap", "walls", "roof")
OPTIONS = ("top_material", "segments", "rings", "lower", "wall")
MATERIALS = {
    "PLAIN": PLAIN,
    "OFFICE": OFFICE,
    "HOMES": HOMES,
    "FURNACE": FURNACE,
    "LIGHT": LIGHT,
    "FOLIAGE": FOLIAGE,
    "METAL": METAL,
    "ROOFING": ROOFING,
}


class PropModel:
    """A prop's description, built once in its own box, ready to be stretched into any number of lots."""

    def __init__(self, name: str, description: dict[str, Any]) -> None:
        self.name = name
        if extra := set(description) - {"kind", "size", "parts"}:
            msg = f"{name}: unknown keys {sorted(extra)}"
            raise ValueError(msg)
        self.kind: str = description["kind"]
        width, length, height = (float(value) for value in description["size"])
        if min(width, length, height) <= 0:
            msg = f"{name}: its size must be more than 0: {description['size']}"
            raise ValueError(msg)
        self.size = (width, length, height)
        mesh = PropMesh()
        for part in description["parts"]:
            self._add_part(mesh, part)
        self.vertices, self.indices = mesh.arrays()

    @staticmethod
    @cache
    def named(name: str) -> "PropModel":
        """Return a prop read from data/models/props/<name>.json, the first time it's needed."""
        text = (data_folder() / PROPS_FOLDER / f"{name}.json").read_text()
        return PropModel(name, json.loads(text))

    def build(self, mesh: PropMesh, prop: Prop) -> None:
        """Add this prop to a mesh, stretched to fit `prop`'s lot and moved to its place."""
        vertices = self.vertices.copy()
        width, length, height = self.size
        if width != length and (width > length) != (prop.width > prop.length):  # a quarter turn
            for a, b in ((0, 1), (3, 4)):
                along = vertices[:, a].copy()
                vertices[:, a] = -vertices[:, b]
                vertices[:, b] = along
            width, length = length, width
        scale = np.array([prop.width / width, prop.length / length, prop.height / height], dtype=np.float32)
        normals = vertices[:, 3:6]
        # The windows keep their size: the wall coordinates are stretched like the wall they're on.
        across = np.hypot(normals[:, 0], normals[:, 1])
        stretched = np.hypot(normals[:, 1] * scale[0], normals[:, 0] * scale[1])
        vertices[:, 10] *= np.where(across > 1e-6, stretched / np.maximum(across, 1e-6), 1.0)
        vertices[:, 11] = np.where(vertices[:, 11] > 0, vertices[:, 11] * scale[2], vertices[:, 11])
        vertices[:, 0:2] *= scale[:2]
        vertices[:, 2] = np.where(vertices[:, 2] > 0, vertices[:, 2] * scale[2], vertices[:, 2])  # SUNK as it is
        normals /= scale
        normals /= np.linalg.norm(normals, axis=1, keepdims=True)
        vertices[:, 0:3] += (prop.x, prop.y, prop.base)
        vertices[:, 12] = (prop.seed % 997) / 997  # the shader picks its lit windows with it
        mesh.add(vertices, self.indices)

    def _add_part(self, mesh: PropMesh, part: dict[str, Any]) -> None:
        shapes = [key for key in part if key in SHAPES]
        if len(shapes) != 1:
            msg = f"{self.name}: a part needs exactly one of {SHAPES}: {part}"
            raise ValueError(msg)
        shape = shapes[0]
        if extra := set(part) - {shape, "material", *COLORS, *OPTIONS}:
            msg = f"{self.name}: unknown keys {sorted(extra)} in {part}"
            raise ValueError(msg)
        options: dict[str, Any] = {key: _tuples(value) for key, value in part.items() if key != shape}
        for key in ("material", "top_material"):
            if key in options:
                options[key] = MATERIALS[options[key]]
        options.setdefault("material", PLAIN)
        try:
            getattr(mesh, shape)(*_tuples(part[shape]), **options)
        except TypeError as error:  # missing or extra arguments
            msg = f"{self.name}: {error}: {part}"
            raise ValueError(msg) from error


@cache
def catalog() -> dict[str, list[PropModel]]:
    """Return every prop in data/models/props/, by kind, in the order of their file names."""
    folder = data_folder() / PROPS_FOLDER
    found: dict[str, list[PropModel]] = {}
    for name in sorted(entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json")):
        model = PropModel.named(name)
        found.setdefault(model.kind, []).append(model)
    return found


def _tuples(value: Any) -> Any:  # noqa: ANN401 - a JSON value of any shape
    """Return the JSON's lists as tuples, all the way down (points, colors, profiles)."""
    return tuple(_tuples(item) for item in value) if isinstance(value, list) else value
