import numpy as np
import pytest

from pewpy.scenery.ground import props
from pewpy.scenery.ground.props.mesh import PropMesh
from pewpy.scenery.ground.settlement import Prop

KINDS = ["antenna", "apron", "barn", "building", "containers", "cooling_tower", "dome", "greenhouse"]
KINDS += ["hangar", "hedge", "house", "pad", "pipes", "plant", "pylon", "radar", "silo", "stack", "tank"]
KINDS += ["tree", "warehouse"]


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


def test_a_strip_without_props_is_empty() -> None:
    vertices, triangles = props.strip_arrays([], 0.2)
    assert len(vertices) == len(triangles) == 0


def test_a_prop_is_one_of_its_kinds_picked_by_its_seed_going_round() -> None:
    barns = props.catalog()["barn"]
    picked, again = PropMesh(), PropMesh()
    props.build(picked, Prop("barn", 0.5, 0.3, 0.08, 0.05, 0.04, 1))
    props.build(again, Prop("barn", 0.5, 0.3, 0.08, 0.05, 0.04, 1 + len(barns)))
    assert np.allclose(picked.arrays()[0][:, :12], again.arrays()[0][:, :12])  # all but the seed
