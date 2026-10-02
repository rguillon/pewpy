import numpy as np
import pytest

from pewpy.scenery import params, props
from pewpy.scenery.props.mesh import PLAIN, PropMesh
from pewpy.scenery.settlement import Prop


@pytest.mark.parametrize("kind", sorted(props.BUILDERS))
@pytest.mark.parametrize("seed", range(12))  # enough for every kind's variants
@pytest.mark.parametrize(("width", "length"), [(0.12, 0.1), (0.1, 0.12)], ids=["wide", "long"])
def test_every_kind_of_prop_has_a_mesh_around_its_footprint(kind, seed, width, length):
    height = 0.3 if kind == "building" else 0.06
    prop = Prop(kind, x=0.5, y=0.3, width=width, length=length, height=height, seed=seed)
    vertices, triangles = props.strip_arrays([prop], first_y=0.2, colors=params.resolve("city").props)
    assert len(triangles) % 3 == 0 and len(triangles) > 0
    assert int(np.max(triangles)) < len(vertices)
    assert np.isfinite(vertices).all()
    assert np.allclose(np.linalg.norm(vertices[:, 3:6], axis=1), 1.0, atol=1e-3)  # proper normals
    # Model space: x as is, depth -y is the height, z up the screen from the strip's top edge.
    xs, heights, zs = vertices[:, 0], -vertices[:, 1], vertices[:, 2]
    reach = max(prop.width, prop.length) / 2 * 1.1 + 0.02  # palms lean, fronds droop past the footprint
    assert float(np.min(xs)) >= 0.5 - reach and float(np.max(xs)) <= 0.5 + reach
    assert float(np.min(heights)) >= -props.SUNK - 1e-6
    # Masts, chimneys, domes and flames (as big as the stack) stick out on top.
    assert float(np.max(heights)) <= prop.height * 1.6 + 0.09 + max(prop.width, prop.length)
    assert float(np.max(-zs)) <= 0.3 - 0.2 + reach


def test_props_of_a_kind_differ_by_their_seed():
    colors = params.resolve("city").props
    for kind in props.BUILDERS:
        shapes = set()
        for seed in range(12):
            vertices, _ = props.strip_arrays([Prop(kind, 0.5, 0.3, 0.12, 0.1, 0.3, seed)], 0.2, colors)
            shapes.add((len(vertices), round(float(vertices[:, :3].sum()), 4)))
        assert len(shapes) > 1, kind


def test_a_strip_without_props_is_empty():
    vertices, triangles = props.strip_arrays([], 0.2, params.resolve("city").props)
    assert len(vertices) == len(triangles) == 0


def test_a_small_warehouse_has_no_room_for_roof_vents():
    colors = params.resolve("city").props
    for seed in range(12):
        vertices, _ = props.strip_arrays([Prop("warehouse", 0.5, 0.3, 0.012, 0.012, 0.03, seed)], 0.2, colors)
        assert np.isfinite(vertices).all()


def test_every_plant_variant_builds():
    colors = params.resolve("city").props
    for seed in range(60):  # some only have a plain roof
        vertices, _ = props.strip_arrays([Prop("plant", 0.5, 0.3, 0.12, 0.1, 0.06, seed)], 0.2, colors)
        assert np.isfinite(vertices).all()


def test_a_shape_turned_to_a_point_needs_no_cap():
    mesh = PropMesh()
    mesh.lathe(0.0, 0.0, [(0.0, 0.01), (0.02, 0.0)], (1.0, 1.0, 1.0), PLAIN, segments=6, cap=(1.0, 0.0, 0.0))
    capped = PropMesh()
    capped.lathe(0.0, 0.0, [(0.0, 0.01), (0.02, 0.005)], (1.0, 1.0, 1.0), PLAIN, segments=6, cap=(1.0, 0.0, 0.0))
    assert len(mesh.arrays()[0]) < len(capped.arrays()[0])
