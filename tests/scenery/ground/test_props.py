import numpy as np
import pytest

from pewpy.scenery.ground import props
from pewpy.scenery.ground.props.mesh import METAL, PLAIN, PropMesh
from pewpy.scenery.ground.props.model import PropModel
from pewpy.scenery.ground.settlement import Prop

KINDS = ["antenna", "apron", "barn", "building", "containers", "cooling_tower", "dome", "greenhouse"]
KINDS += ["hangar", "hedge", "house", "pad", "pipes", "plant", "pylon", "radar", "silo", "stack", "tank"]
KINDS += ["tree", "warehouse"]


def test_every_kind_the_grounds_ask_for_has_props() -> None:
    assert sorted(props.catalog()) == sorted(KINDS)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize(("width", "length"), [(0.12, 0.1), (0.1, 0.12)], ids=["wide", "long"])
def test_every_prop_has_a_mesh_around_its_footprint(kind: str, width: float, length: float) -> None:
    height = 0.3 if kind == "building" else 0.06
    for seed in range(len(props.catalog()[kind])):
        prop = Prop(kind, x=0.5, y=0.3, width=width, length=length, height=height, seed=seed)
        vertices, triangles = props.strip_arrays([prop], first_y=0.2)
        assert len(triangles) % 3 == 0
        assert len(triangles) > 0
        assert int(np.max(triangles)) < len(vertices)
        assert np.isfinite(vertices).all()
        assert np.allclose(np.linalg.norm(vertices[:, 3:6], axis=1), 1.0, atol=1e-3)  # proper normals
        # Model space: x as is, depth -y is the height, z up the screen from the strip's top edge.
        xs, heights, zs = vertices[:, 0], -vertices[:, 1], vertices[:, 2]
        reach = max(prop.width, prop.length) / 2 * 1.4  # palms lean, fronds droop past the footprint
        assert float(np.min(xs)) >= 0.5 - reach
        assert float(np.max(xs)) <= 0.5 + reach
        assert float(np.min(heights)) >= -props.SUNK - 1e-6
        # Masts, chimneys, flames, pipe racks and parked craft stick out on top.
        assert float(np.max(heights)) <= prop.height * 5
        assert float(np.max(-zs)) <= 0.3 - 0.2 + reach


def test_a_kind_picks_its_props_by_the_seed() -> None:
    barns = props.catalog()["barn"]
    assert len(barns) > 1
    shapes = set()
    for seed in range(len(barns)):
        vertices, _ = props.strip_arrays([Prop("barn", 0.5, 0.3, 0.08, 0.05, 0.04, seed)], 0.2)
        shapes.add((len(vertices), round(float(vertices[:, :3].sum()), 4)))
    assert len(shapes) == len(barns)


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
    assert np.isclose(vertices[:, 2].min(), -props.SUNK)  # sunk as deep, however tall
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


def test_a_strip_without_props_is_empty() -> None:
    vertices, triangles = props.strip_arrays([], 0.2)
    assert len(vertices) == len(triangles) == 0


def test_a_shape_turned_to_a_point_needs_no_cap() -> None:
    mesh = PropMesh()
    mesh.lathe(0.0, 0.0, [(0.0, 0.01), (0.02, 0.0)], (1.0, 1.0, 1.0), PLAIN, segments=6, cap=(1.0, 0.0, 0.0))
    capped = PropMesh()
    capped.lathe(0.0, 0.0, [(0.0, 0.01), (0.02, 0.005)], (1.0, 1.0, 1.0), PLAIN, segments=6, cap=(1.0, 0.0, 0.0))
    assert len(mesh.arrays()[0]) < len(capped.arrays()[0])


def test_a_gabled_roof_runs_along_the_longer_side() -> None:
    for x1, y1 in ((2.0, 1.0), (1.0, 2.0)):
        mesh = PropMesh()
        mesh.gabled(0.0, x1, 0.0, y1, 0.0, 1.0, 1.5, (1.0, 1.0, 1.0), (0.5, 0.5, 0.5), PLAIN)
        vertices, _ = mesh.arrays()
        ridge = vertices[np.isclose(vertices[:, 2], 1.5)]
        along_x = x1 > y1
        assert np.ptp(ridge[:, 0]) == pytest.approx(x1 if along_x else 0.0)
        assert np.ptp(ridge[:, 1]) == pytest.approx(0.0 if along_x else y1)
