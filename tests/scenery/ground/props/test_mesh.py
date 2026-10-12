import numpy as np
import pytest

from pewpy.scenery.ground.props.mesh import PLAIN, PropMesh


def test_a_mesh_counts_its_vertices_as_they_are_added() -> None:
    mesh = PropMesh()
    corners = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.0, 1.0)]
    mesh.quad(corners, (0.0, -1.0, 0.0), (1.0, 1.0, 1.0), PLAIN)
    mesh.quad(corners, (0.0, -1.0, 0.0), (1.0, 1.0, 1.0), PLAIN)
    vertices, indices = mesh.arrays()
    assert vertices.shape == (8, 14)
    assert len(indices) == 12
    assert int(indices.max()) == 7  # the second quad's triangles point at its own vertices


def test_a_box_has_its_walls_and_top_but_no_bottom() -> None:
    mesh = PropMesh()
    mesh.box(0.0, 1.0, 0.0, 1.0, 0.0, 1.0, (1.0, 1.0, 1.0), PLAIN)
    vertices, _ = mesh.arrays()
    normals = {tuple(np.round(normal).astype(int)) for normal in vertices[:, 3:6]}
    assert (0, 0, 1) in normals
    assert (0, 0, -1) not in normals


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
