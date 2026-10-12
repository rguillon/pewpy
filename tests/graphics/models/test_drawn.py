import json
from collections.abc import Callable
from functools import partial

import pytest
from panda3d.core import GeomNode, NodePath

from pewpy import config
from pewpy.data import data_folder
from pewpy.data import read_model as model_file
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.kinds import ENEMIES
from pewpy.game.player import Player
from pewpy.game.weapons.bullets import Missile
from pewpy.graphics.models.built.turret import turret_model
from pewpy.graphics.models.drawings.files import drawing_size, parse_voxels, read_drawing
from pewpy.graphics.models.drawn import BUILT_MODELS, drawing_model, drawn_model, model, voxel_model
from tests.graphics.models.meshes import WHITE, all_points, assert_closed_and_facing_out

DRAWINGS = ["player", "drone", "weaver", "diver", "gunship", "swarmer", "sniper", "mine_layer", "mine",
            "shield_carrier", "splitter", "missile"]  # fmt: skip


@pytest.mark.parametrize("drawing", DRAWINGS[:5])
def test_every_model_is_a_closed_surface_facing_out(drawing: str) -> None:
    node = model(drawing).node()
    assert isinstance(node, GeomNode)
    assert_closed_and_facing_out(node)


@pytest.mark.parametrize("drawing", DRAWINGS)
def test_ship_models_are_more_than_a_cube(drawing: str) -> None:
    assert len(all_points(model(drawing))) > 3 * 12


@pytest.mark.parametrize("kind", ["Player", "Missile", *ENEMIES])
def test_ship_models_are_meant_to_be_about_the_size_of_their_hitbox(kind: str) -> None:
    """A model's "size" (what new models of it are made to, see pewpy.generators.models.sized) must fit its hitbox.

    The model built in code (the turret) is drawn to it. An enemy sized by its model's cubes ("voxels") is
    its drawing whatever its "size" (see test_kinds).
    """
    if "voxels" in json.loads((data_folder() / "enemies" / "fleet.json").read_text()).get(kind, {}):
        return
    entity = {"Player": Player, "Missile": Missile}.get(kind, partial(Enemy.of_kind, kind))()
    drawing = entity.ship.drawing if isinstance(entity, Player) else entity.drawing
    if drawing in BUILT_MODELS:
        points = all_points(model(drawing))
        width = max(point.x for point in points) - min(point.x for point in points)
        height = max(point.z for point in points) - min(point.z for point in points)
    else:
        data, _ = read_drawing(drawing)
        width, height = drawing_size(data, parse_voxels(data))
    assert width == pytest.approx(entity.width, rel=0.2)
    assert height <= entity.height * 1.2
    assert max(width, height) == pytest.approx(max(entity.width, entity.height), rel=0.2)


def test_every_drawing_has_the_same_cubes() -> None:
    """Models aren't stretched: a drawing's voxel is config.MODEL_VOXEL, whatever its size."""
    for drawing in ("swarmer", "player", "player_light", "gunship"):
        points = all_points(model(drawing))
        xs = sorted({round(point.x / config.MODEL_VOXEL, 3) for point in points})
        assert all(abs(x - round(x * 2) / 2) < 1e-3 for x in xs)  # corners on the half-cube grid


def test_a_voxel_model_has_its_middle_at_the_origin() -> None:
    points = all_points(voxel_model("bar", ["xxx"], {"x": (WHITE, 1)}))
    assert min(point.x for point in points) == pytest.approx(-1.5 * config.MODEL_VOXEL)
    assert max(point.x for point in points) == pytest.approx(1.5 * config.MODEL_VOXEL)


def test_a_model_is_built_from_its_data_too() -> None:
    data = {"layers": [["a"]], "palette": {"a": {"color": [1, 1, 1]}}, "engines": [
        {"x": 0, "y": 0, "width": 1, "length": 2, "towards": "top"}
    ]}  # fmt: skip
    built = drawn_model("new", data)
    assert built.getName() == "new"
    assert not built.find("**/flame").isEmpty()


def test_ships_with_engines_have_flames() -> None:
    for name in ("player", "missile"):
        engines = model_file(name)[0]["engines"]
        assert engines
        assert len(drawing_model(name).findAllMatches("**/flame")) == len(engines)


@pytest.mark.parametrize(("drawing", "build"), BUILT_MODELS.items())
def test_some_models_are_built_in_code(drawing: str, build: Callable[[], NodePath]) -> None:
    assert build is turret_model
    assert not model(drawing).find("**/barrel").isEmpty()
