import numpy as np
import pytest

from pewpy.scenery import params, props
from pewpy.scenery.settlement import Prop


@pytest.mark.parametrize("kind", sorted(props.BUILDERS))
@pytest.mark.parametrize("seed", range(12))  # enough for every kind's variants
def test_every_kind_of_prop_has_a_mesh_around_its_footprint(kind, seed):
    prop = Prop(kind, x=0.5, y=0.3, width=0.12, length=0.1, height=0.3 if kind == "building" else 0.06, seed=seed)
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
