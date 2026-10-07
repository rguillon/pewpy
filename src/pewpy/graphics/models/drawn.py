"""The models of the drawings, and which model a drawing has."""

from collections.abc import Callable
from typing import Any

from panda3d.core import NodePath

from pewpy import config
from pewpy.graphics.models.built.turret import turret_model
from pewpy.graphics.models.drawings.engines import parse_engines
from pewpy.graphics.models.drawings.files import parse_voxels, read_drawing
from pewpy.graphics.models.flames import add_flame
from pewpy.graphics.models.mesh.builder import MeshBuilder
from pewpy.graphics.models.types import Palette


def voxel_model(name: str, rows: list[str], palette: Palette) -> NodePath:
    """Build a drawing's model in world units: every cube is config.MODEL_VOXEL, the drawing's middle at the origin."""
    mesh = MeshBuilder()
    mesh.voxels(rows, palette, config.MODEL_VOXEL)
    return NodePath(mesh.build(name))


def drawing_model(name: str) -> NodePath:
    """Build the drawing's voxel model, with a flame (a child node named "flame") for each of its engines."""
    data, source = read_drawing(name)
    return drawn_model(name, data, source)


def drawn_model(name: str, data: Any, source: str = "drawing") -> NodePath:  # noqa: ANN401 - JSON
    """Build the voxel model of a drawing's data (as its file has it), with its engines' flames, named `name`."""
    voxels = parse_voxels(data, source)
    mesh = MeshBuilder()
    mesh.drawn_cells(voxels, voxels.size)
    model = NodePath(mesh.build(name))
    for engine in parse_engines(data, source):
        add_flame(model, engine, (voxels.width, voxels.height), voxels.size)
    return model


def model(drawing: str) -> NodePath:
    """Return the model of a drawing (models/<group>/<drawing>.json).

    The turret's is built with a barrel the game turns (see BUILT_MODELS). Models point down the screen
    (-Z), so the game can turn them with `facing_roll`.
    """
    built = BUILT_MODELS.get(drawing)
    return built() if built else drawing_model(drawing)


BUILT_MODELS: dict[str, Callable[[], NodePath]] = {"turret": turret_model}
