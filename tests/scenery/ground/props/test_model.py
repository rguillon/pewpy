import numpy as np
import pytest

from pewpy.scenery.ground.props.mesh import METAL, PLAIN, SUNK, PropMesh
from pewpy.scenery.ground.props.model import PropModel, catalog
from pewpy.scenery.ground.settlement import Prop

KINDS = ["antenna", "apron", "barn", "building", "containers", "cooling_tower", "dome", "greenhouse"]
KINDS += ["hangar", "hedge", "house", "pad", "pipes", "plant", "pylon", "radar", "silo", "stack", "tank"]
KINDS += ["tree", "warehouse"]


def test_every_kind_the_grounds_ask_for_has_props() -> None:
    assert sorted(catalog()) == sorted(KINDS)


def test_a_prop_is_read_once_from_its_file() -> None:
    first = catalog()["barn"][0]
    assert PropModel.named(first.name) is first
    assert first.kind == "barn"


def test_a_prop_is_stretched_to_its_lot_and_turned_to_lie_along_it() -> None:
    model = PropModel(
        "test", {"kind": "test", "size": [2, 1, 1], "parts": [{"box": [-1, 1, -0.5, 0.5, 0, 1], "color": [1, 1, 1]}]}
    )
    mesh = PropMesh()
    model.build(mesh, Prop("test", 10.0, 20.0, width=0.5, length=4.0, height=3.0, seed=0))
    vertices, _ = mesh.arrays()
    assert np.isclose(vertices[:, 0].min(), 9.75)
    assert np.isclose(vertices[:, 0].max(), 10.25)
    assert np.isclose(vertices[:, 1].min(), 18.0)
    assert np.isclose(vertices[:, 1].max(), 22.0)
    assert np.isclose(vertices[:, 2].max(), 3.0)
    assert np.isclose(vertices[:, 2].min(), -SUNK)  # sunk as deep, however tall
    # The wall coordinates are in world units: the long walls are 4 long, the short ones 0.5, every wall 3 high.
    walls = vertices[np.abs(vertices[:, 5]) < 0.5]
    assert sorted({round(float(u), 4) for u in walls[:, 10]}) == [0.0, 0.5, 4.0]
    assert np.isclose(walls[:, 11].max(), 3.0)


def test_a_prop_reads_its_colors_materials_and_options() -> None:
    model = PropModel(
        "test",
        {
            "kind": "test",
            "size": [1, 1, 1],
            "parts": [
                {"cylinder": [0, 0, 0.5, 0, 1], "color": [1, 0, 0], "material": "METAL", "segments": 6},
                {"ellipsoid": [0, 0, 1, [0.5, 0.5, 0.2]], "color": [0, 1, 0], "lower": 0},
            ],
        },
    )
    vertices = model.vertices
    assert {tuple(color) for color in vertices[:, 6:9].tolist()} == {(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)}
    assert {int(material) for material in vertices[:, 9]} == {METAL, PLAIN}


@pytest.mark.parametrize(
    "description",
    [
        {"kind": "test", "size": [1, 1, 1], "parts": [], "colors": {}},
        {"kind": "test", "size": [1, 0, 1], "parts": []},
        {"kind": "test", "size": [1, 1, 1], "parts": [{"color": [1, 1, 1]}]},
        {"kind": "test", "size": [1, 1, 1], "parts": [{"box": [0, 1, 0, 1, 0, 1], "disc": [0, 0, 1, 1]}]},
        {"kind": "test", "size": [1, 1, 1], "parts": [{"box": [0, 1, 0, 1, 0, 1], "colour": [1, 1, 1]}]},
        {"kind": "test", "size": [1, 1, 1], "parts": [{"box": [0, 1, 0, 1, 0, 1]}]},
    ],
    ids=["unknown key", "flat", "no shape", "two shapes", "unknown option", "no color"],
)
def test_a_wrong_description_is_refused(description: dict[str, object]) -> None:
    with pytest.raises(ValueError, match="test"):
        PropModel("test", description)


def test_a_part_with_the_wrong_numbers_says_which_prop() -> None:
    with pytest.raises(ValueError, match=r"test: .*box"):
        PropModel("test", {"kind": "test", "size": [1, 1, 1], "parts": [{"box": [0, 1], "color": [1, 1, 1]}]})
