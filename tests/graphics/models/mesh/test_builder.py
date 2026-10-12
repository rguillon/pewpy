import numpy as np
import pytest
from panda3d.core import Vec3

from pewpy.graphics.models.drawings.voxels import voxel_cells
from pewpy.graphics.models.mesh.builder import GLOW_UVS, NO_BEVEL, QUAD_UVS, MeshBuilder
from pewpy.graphics.models.mesh.voxel_faces import FACE_DIRECTIONS
from tests.graphics.models.meshes import WHITE, assert_closed_and_facing_out, surface, triangles_of, volume


def test_ellipsoid_faces_away_from_its_center() -> None:
    mesh = MeshBuilder()
    center = Vec3(0.1, 0.2, 0.3)
    mesh.ellipsoid(center, Vec3(0.1, 0.2, 0.3), (1, 1, 1, 1))
    for corners, normal in triangles_of(mesh.build("shapes")):
        assert normal.dot((corners[0] + corners[1] + corners[2]) / 3 - center) > 0


def test_a_box_is_closed_and_faces_out() -> None:
    mesh = MeshBuilder()
    mesh.box(Vec3(0.5, 0, 0), Vec3(1, 2, 3), WHITE)
    assert len(mesh.triangles) == 12
    assert_closed_and_facing_out(mesh.build("box"))
    assert volume(mesh) == pytest.approx(6.0)


def test_a_prism_is_its_outline_pushed_back() -> None:
    mesh = MeshBuilder()
    mesh.prism([(0, 0), (1, 0), (1, 1), (0, 1)], -0.5, 0.5, WHITE)
    assert_closed_and_facing_out(mesh.build("prism"))
    assert volume(mesh) == pytest.approx(1.0)


def test_touching_voxels_hide_their_shared_faces() -> None:
    mesh = MeshBuilder()
    mesh.voxels(["xx"], {"x": (WHITE, 1)}, 1.0)
    triangles = triangles_of(mesh.build("pair"))
    assert len(triangles) == 2 * 6  # a 2 x 1 x 1 box: the shared faces are hidden, the flat sides merged
    for corners, normal in triangles:
        winding = (corners[1] - corners[0]).cross(corners[2] - corners[0])
        assert winding.dot(normal) > 0
        assert normal.dot((corners[0] + corners[1] + corners[2]) / 3) > 0  # outward from the pair's center


def test_lone_voxel_is_not_darkened() -> None:
    mesh = MeshBuilder()
    mesh.voxels(["x"], {"x": (WHITE, 1)}, 1.0)
    assert {color for triangle in mesh.triangles for _, color, _ in triangle} == {WHITE}


def test_voxel_corners_next_to_other_voxels_are_darkened() -> None:
    # The top face of the bottom-right voxel touches the voxel above-left of it along one edge.
    mesh = MeshBuilder()
    mesh.voxels(["x.", "xx"], {"x": (WHITE, 1)}, 1.0)
    brightness = {color[0] for triangle in mesh.triangles for _, color, _ in triangle}
    assert min(brightness) < 1.0
    assert max(brightness) == 1.0


def test_flat_runs_of_alike_faces_become_one_rectangle_counting_its_cubes() -> None:
    mesh = MeshBuilder()
    mesh.voxels(["xxx", "xxx"], {"x": (WHITE, 1)}, 1.0)  # a 3 x 2 plate, one cube thick
    assert len(mesh.triangles) == 2 * 6  # still a box: one rectangle per side
    uvs = {uv for triangle in mesh.triangles for _, _, uv in triangle}
    assert (3.0, 2.0) in uvs  # the front: 3 cubes across, 2 up, so the shader bevels each cube


def test_merged_faces_cover_exactly_the_faces_of_the_cubes() -> None:
    """Merging changes the triangles, not the surface: per direction, the area is the number of visible cube faces."""
    rows = ["x.x.x", "xxxxx", "xxxxx", "x...x"]  # no staircase: nothing sloped
    palette = {"x": (WHITE, 3)}
    mesh = MeshBuilder()
    mesh.voxels(rows, palette, 1.0)
    _, normals, areas = surface(mesh)
    cells = voxel_cells(rows, palette)
    for direction in FACE_DIRECTIONS:
        dx, dy, dz = direction
        visible = sum((column + dx, row - dz, layer + dy) not in cells for column, row, layer in cells)
        facing = (np.round(normals) == direction).all(axis=1)
        assert np.linalg.norm(areas[facing], axis=1).sum() == pytest.approx(visible)


@pytest.mark.parametrize("rows", [["##", "##"], [".#.", "###"], ["#..", "###"], ["#.#", "###"]])
def test_square_corners_and_spikes_stay_square(rows: list[str]) -> None:
    mesh = MeshBuilder()
    mesh.voxels(rows, {"#": (WHITE, 1)}, 1.0)
    _, normals, _ = surface(mesh)
    assert (np.abs(normals).max(axis=1) == 1).all()
    assert volume(mesh) == pytest.approx(sum(row.count("#") for row in rows))


def test_faces_only_merge_where_their_shading_stays_the_same() -> None:
    """Along a ledge, the faces below it are darker near it: they merge along the ledge, not away from it."""
    mesh = MeshBuilder()
    mesh.voxels(["xxx", "xxx", "yyy"], {"x": (WHITE, 1), "y": (WHITE, 3)}, 1.0)  # "y" sticks out in front
    front = [
        triangle for triangle in mesh.triangles if all(corner.y == pytest.approx(-0.5) for corner, _, _ in triangle)
    ]
    shades = {color[0] for triangle in front for _, color, _ in triangle}
    assert len(shades) > 1  # darkened next to the thicker row
    # The row above is one rectangle; the darkened row splits where its shading changes: its two ends, with fewer
    # neighbors, are shaded differently from its middle. 4 rectangles instead of 6 faces.
    assert len(front) == 2 * 4


def test_only_voxel_faces_get_bevel_coordinates() -> None:
    voxels = MeshBuilder()
    voxels.voxels(["x"], {"x": (WHITE, 1)}, 1.0)
    assert {uv for triangle in voxels.triangles for _, _, uv in triangle} == set(QUAD_UVS)  # one cube
    box = MeshBuilder()
    box.box(Vec3(0, 0, 0), Vec3(1, 1, 1), WHITE)
    assert {uv for triangle in box.triangles for _, _, uv in triangle} == {NO_BEVEL}


def test_glowing_voxel_faces_are_marked_for_the_shader() -> None:
    mesh = MeshBuilder()
    mesh.cells({(0, 0, 0): WHITE, (1, 0, 0): WHITE}, 1.0, Vec3(0, 0, 0), glowing=frozenset({(1, 0, 0)}))
    uvs = {uv for triangle in mesh.triangles for _, _, uv in triangle}
    assert uvs == set(QUAD_UVS) | set(GLOW_UVS)


def test_a_quad_splits_along_its_brighter_diagonal() -> None:
    corners = (Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(1, 0, 1), Vec3(0, 0, 1))
    for brightness, diagonal in (((0.5, 1, 0.5, 1), (1, 3)), ((1, 0.5, 1, 0.5), (0, 2))):
        mesh = MeshBuilder()
        mesh.quad(*corners, (1, 1, 1, 1), Vec3(0, 1, 0), brightness)
        triangles = triangles_of(mesh.build("quad"))
        shared = set.intersection(*({tuple(round(v, 6) for v in point) for point in points} for points, _ in triangles))
        assert shared == {tuple(corners[index]) for index in diagonal}


def test_an_empty_mesh_builds_an_empty_node() -> None:
    mesh = MeshBuilder()
    mesh.cells({}, 1.0, Vec3(0, 0, 0))
    assert mesh.build("nothing").getGeom(0).getVertexData().getNumRows() == 0
