import json
import math
from collections.abc import Callable
from functools import partial
from typing import Any

import numpy as np
import pytest
from panda3d.core import GeomNode, GeomVertexReader, NodePath, Vec3

from pewpy import config
from pewpy.data import MODEL_GROUPS, data_folder
from pewpy.data import read_model as model_file
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.kinds import ENEMIES
from pewpy.game.player import Player
from pewpy.game.weapons.bullets import Missile
from pewpy.graphics import models
from pewpy.graphics.models.drawings.files import read_drawing
from pewpy.graphics.models.types import Palette

SHIP_MODELS = [
    partial(models.model, "player"),
    partial(models.model, "drone"),
    partial(models.model, "weaver"),
    partial(models.model, "diver"),
    partial(models.model, "gunship"),
    models.turret_model,
    partial(models.model, "swarmer"),
    partial(models.model, "sniper"),
    partial(models.model, "mine_layer"),
    partial(models.model, "mine"),
    partial(models.model, "shield_carrier"),
    partial(models.model, "splitter"),
    partial(models.model, "missile"),
    models.repair_model,
    lambda: models.pickup_model("B", (1, 1, 0, 1)),
]


def voxels_of(drawing: str) -> models.Voxels:
    """Read a drawing's cubes from its file."""
    return models.parse_voxels(*read_drawing(drawing))


def triangles_of(node: GeomNode) -> list[tuple[list[Vec3], Vec3]]:
    """(corners, stored normal) for every triangle of a GeomNode."""
    result = []
    for geom_index in range(node.getNumGeoms()):
        geom = node.getGeom(geom_index)
        vertices = GeomVertexReader(geom.getVertexData(), "vertex")
        normals = GeomVertexReader(geom.getVertexData(), "normal")
        triangles = geom.getPrimitive(0).decompose()
        for index in range(triangles.getNumPrimitives()):
            start = triangles.getPrimitiveStart(index)
            corners = []
            for corner in range(3):
                vertices.setRow(triangles.getVertex(start + corner))
                corners.append(Vec3(vertices.getData3()))
            normals.setRow(triangles.getVertex(start))
            result.append((corners, Vec3(normals.getData3())))
    return result


def all_points(model: NodePath) -> list[Vec3]:
    """Every corner of the model's meshes, in their own space: engine flames left out (they stick out)."""
    points = []
    for path in [model, *model.findAllMatches("**/+GeomNode")]:
        if not isinstance(path.node(), GeomNode) or "flame" in str(path).split("/"):
            continue
        node = path.node()
        assert isinstance(node, GeomNode)
        for corners, _ in triangles_of(node):
            points += corners
    return points


RED = [1.0, 0.0, 0.0]
BLUE = [0.0, 0.0, 1.0]


def test_cube_faces_outward() -> None:
    cube = models.make_cube()
    triangles = triangles_of(cube)
    assert len(triangles) == 12
    for corners, normal in triangles:
        winding = (corners[1] - corners[0]).cross(corners[2] - corners[0])
        assert winding.dot(normal) > 0  # counter-clockwise seen from outside
        center = (corners[0] + corners[1] + corners[2]) / 3
        assert normal.dot(center) > 0  # and pointing away from the cube's center


def test_ellipsoid_faces_away_from_its_center() -> None:
    mesh = models.MeshBuilder()
    center = Vec3(0.1, 0.2, 0.3)
    mesh.ellipsoid(center, Vec3(0.1, 0.2, 0.3), (1, 1, 1, 1))
    for corners, normal in triangles_of(mesh.build("shapes")):
        assert normal.dot((corners[0] + corners[1] + corners[2]) / 3 - center) > 0


WHITE = (1.0, 1.0, 1.0, 1.0)


def test_touching_voxels_hide_their_shared_faces() -> None:
    mesh = models.MeshBuilder()
    mesh.voxels(["xx"], {"x": (WHITE, 1)}, 1.0)
    triangles = triangles_of(mesh.build("pair"))
    assert len(triangles) == 2 * 6  # a 2 x 1 x 1 box: the shared faces are hidden, the flat sides merged
    for corners, normal in triangles:
        winding = (corners[1] - corners[0]).cross(corners[2] - corners[0])
        assert winding.dot(normal) > 0
        assert normal.dot((corners[0] + corners[1] + corners[2]) / 3) > 0  # outward from the pair's center


def test_lone_voxel_is_not_darkened() -> None:
    mesh = models.MeshBuilder()
    mesh.voxels(["x"], {"x": (WHITE, 1)}, 1.0)
    assert {color for triangle in mesh.triangles for _, color, _ in triangle} == {WHITE}


def test_voxel_corners_next_to_other_voxels_are_darkened() -> None:
    # The top face of the bottom-right voxel touches the voxel above-left of it along one edge.
    mesh = models.MeshBuilder()
    mesh.voxels(["x.", "xx"], {"x": (WHITE, 1)}, 1.0)
    brightness = {color[0] for triangle in mesh.triangles for _, color, _ in triangle}
    assert min(brightness) < 1.0
    assert max(brightness) == 1.0


@pytest.mark.parametrize(
    ("side_a", "side_b", "corner", "expected"),
    [
        (False, False, False, models.OCCLUSION_BRIGHTNESS[0]),
        (False, False, True, models.OCCLUSION_BRIGHTNESS[1]),
        (True, False, True, models.OCCLUSION_BRIGHTNESS[2]),
        (True, True, False, models.OCCLUSION_BRIGHTNESS[3]),  # both sides: fully tucked in
    ],
)
def test_occlusion_counts_the_voxels_in_front_of_a_corner(
    side_a: bool, side_b: bool, corner: bool, expected: float
) -> None:
    level = models.occlusion_level(np.array([side_a]), np.array([side_b]), np.array([corner]))
    assert models.OCCLUSION_BRIGHTNESS[level[0]] == expected


def test_flat_runs_of_alike_faces_become_one_rectangle_counting_its_cubes() -> None:
    mesh = models.MeshBuilder()
    mesh.voxels(["xxx", "xxx"], {"x": (WHITE, 1)}, 1.0)  # a 3 x 2 plate, one cube thick
    assert len(mesh.triangles) == 2 * 6  # still a box: one rectangle per side
    uvs = {uv for triangle in mesh.triangles for _, _, uv in triangle}
    assert (3.0, 2.0) in uvs  # the front: 3 cubes across, 2 up, so the shader bevels each cube


def surface(mesh: models.MeshBuilder) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Every triangle's corners (n, 3, 3), stored normal (n, 3) and area times its winding's direction (n, 3)."""
    corners, normals, _, _ = mesh._arrays()
    return corners, normals, np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0]) / 2


def volume(mesh: models.MeshBuilder) -> float:
    """Return the volume a closed mesh holds (divergence theorem)."""
    corners, _, areas = surface(mesh)
    return float(np.einsum("ij,ij->", corners.mean(axis=1), areas) / 3)


def test_merged_faces_cover_exactly_the_faces_of_the_cubes() -> None:
    """Merging changes the triangles, not the surface: per direction, the area is the number of visible cube faces."""
    rows = ["x.x.x", "xxxxx", "xxxxx", "x...x"]  # no staircase: nothing sloped
    palette: Palette = {"x": (WHITE, 3)}
    mesh = models.MeshBuilder()
    mesh.voxels(rows, palette, 1.0)
    _, normals, areas = surface(mesh)
    cells = models.voxel_cells(rows, palette)
    for direction in models.FACE_DIRECTIONS:
        dx, dy, dz = direction
        visible = sum((column + dx, row - dz, layer + dy) not in cells for column, row, layer in cells)
        facing = (np.round(normals) == direction).all(axis=1)
        assert np.linalg.norm(areas[facing], axis=1).sum() == pytest.approx(visible)


def test_staircases_become_45_degree_slopes() -> None:
    mesh = models.MeshBuilder()
    mesh.voxels(["..##", ".###", "####"], {"#": (WHITE, 1)}, 1.0)
    _, normals, _ = surface(mesh)
    slanted = normals[np.abs(normals).max(axis=1) < 0.9]
    assert len(slanted)
    assert np.allclose(slanted, [-math.sqrt(0.5), 0, math.sqrt(0.5)])  # up and left: the stair goes up to the right
    assert volume(mesh) == pytest.approx(9 - 2 * 0.5)  # the outer corner of each of the 2 steps is cut in half


def test_a_thicker_part_slopes_down_to_a_thinner_one() -> None:
    mesh = models.MeshBuilder()
    mesh.voxels(["xxxxx", "xcccx", "xcccx", "xxxxx"], {"x": (WHITE, 1), "c": (WHITE, 3)}, 1.0)
    _, normals, _ = surface(mesh)
    assert np.isclose(np.abs(normals[:, 1]), math.sqrt(0.5)).any()  # sloped towards the camera and away


@pytest.mark.parametrize("rows", [["##", "##"], [".#.", "###"], ["#..", "###"], ["#.#", "###"]])
def test_square_corners_and_spikes_stay_square(rows: list[str]) -> None:
    mesh = models.MeshBuilder()
    mesh.voxels(rows, {"#": (WHITE, 1)}, 1.0)
    _, normals, _ = surface(mesh)
    assert (np.abs(normals).max(axis=1) == 1).all()
    assert volume(mesh) == pytest.approx(sum(row.count("#") for row in rows))


@pytest.mark.parametrize("build", [*SHIP_MODELS[:6], partial(models.distant_planet_model, ((0.2, 0.2, 0.2, 1.0),))])
def test_every_model_is_a_closed_surface_facing_out(build: Callable[[], NodePath]) -> None:
    """Slopes leave no hole: the faces add up to nothing (closed), every triangle wound the way its normal says."""
    node = build().node()
    assert isinstance(node, GeomNode)
    triangles = triangles_of(node)
    areas = [(b - a).cross(c - a) for (a, b, c), _ in triangles]
    assert sum(areas, Vec3()).length() < 1e-5 * sum(area.length() for area in areas)  # corners are stored as float32
    for (a, b, c), normal in triangles:
        assert (b - a).cross(c - a).dot(normal) > 0


def test_faces_only_merge_where_their_shading_stays_the_same() -> None:
    """Along a ledge, the faces below it are darker near it: they merge along the ledge, not away from it."""
    mesh = models.MeshBuilder()
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
    voxels = models.MeshBuilder()
    voxels.voxels(["x"], {"x": (WHITE, 1)}, 1.0)
    assert {uv for triangle in voxels.triangles for _, _, uv in triangle} == set(models.QUAD_UVS)  # one cube
    box = models.MeshBuilder()
    box.box(Vec3(0, 0, 0), Vec3(1, 1, 1), WHITE)
    assert {uv for triangle in box.triangles for _, _, uv in triangle} == {models.NO_BEVEL}
    assert models.make_cube().getGeom(0).getVertexData().hasColumn("texcoord")


def test_glowing_voxel_faces_are_marked_for_the_shader() -> None:
    mesh = models.MeshBuilder()
    mesh.cells({(0, 0, 0): WHITE, (1, 0, 0): WHITE}, 1.0, Vec3(0, 0, 0), glowing=frozenset({(1, 0, 0)}))
    uvs = {uv for triangle in mesh.triangles for _, _, uv in triangle}
    assert uvs == set(models.QUAD_UVS) | set(models.GLOW_UVS)


PLANET = ((0.16, 0.15, 0.15, 1.0), (0.2, 0.18, 0.16, 1.0))


def test_the_distant_planet_fits_the_unit_box() -> None:
    points = all_points(models.distant_planet_model(PLANET))
    for axis in range(3):
        assert min(point[axis] for point in points) >= -0.5 - 1e-6
        assert max(point[axis] for point in points) <= 0.5 + 1e-6


def test_voxel_thickness_is_centered_on_the_depth() -> None:
    cells = models.voxel_cells(["a", "b"], {"a": (WHITE, 1), "b": (WHITE, 5)})
    assert sorted(layer for column, row, layer in cells if row == 1) == [-2, -1, 0, 1, 2]
    assert [layer for column, row, layer in cells if row == 0] == [0]


@pytest.mark.parametrize(
    ("rows", "palette"), [(["ab", "a"], {"a": (WHITE, 1), "b": (WHITE, 1)}), (["a"], {"a": (WHITE, 2)})]
)
def test_bad_voxel_drawings_are_rejected(rows: list[str], palette: Palette) -> None:
    with pytest.raises(ValueError, match="must"):
        models.voxel_cells(rows, palette)


@pytest.mark.parametrize("build", SHIP_MODELS, ids=lambda build: getattr(build, "args", ("pickup",))[0])
def test_ship_models_are_more_than_a_cube(build: Callable[[], NodePath]) -> None:
    assert len(all_points(build())) > 3 * 12


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
    if drawing in models.BUILT_MODELS:
        points = all_points(models.model(drawing))
        width = max(point.x for point in points) - min(point.x for point in points)
        height = max(point.z for point in points) - min(point.z for point in points)
    else:
        data, _ = read_drawing(drawing)
        width, height = models.drawing_size(data, models.parse_voxels(data))
    assert width == pytest.approx(entity.width, rel=0.2)
    assert height <= entity.height * 1.2
    assert max(width, height) == pytest.approx(max(entity.width, entity.height), rel=0.2)


def test_every_drawing_has_the_same_cubes() -> None:
    """Models aren't stretched: a drawing's voxel is config.MODEL_VOXEL, whatever its size."""
    for drawing in ("swarmer", "player", "player_light", "gunship"):
        cube = voxels_of(drawing).size  # config.MODEL_VOXEL
        points = all_points(models.model(drawing))
        xs = sorted({round(point.x / cube, 3) for point in points})
        assert all(abs(x - round(x * 2) / 2) < 1e-3 for x in xs)  # corners on the half-cube grid


def test_turret_has_a_barrel_to_aim() -> None:
    assert not models.turret_model().find("**/barrel").isEmpty()


@pytest.mark.parametrize(("dx", "dz"), [(0, -1), (1, 0), (-1, 0), (0, 1), (1, -1), (-0.3, 0.7)])
def test_facing_roll_points_the_model_along_the_direction(dx: float, dz: float) -> None:
    root = NodePath("root")
    model = root.attachNewNode("model")
    model.setR(models.facing_roll(dx, dz))
    front = root.getRelativeVector(model, Vec3(0, 0, -1))  # models point down the screen
    length = math.hypot(dx, dz)
    assert front.x == pytest.approx(dx / length, abs=1e-5)
    assert front.z == pytest.approx(dz / length, abs=1e-5)


def test_main_colors_are_what_most_of_a_model_is_made_of() -> None:
    red, blue = (1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0)
    model = models.voxel_model("test", ["rrr", "rbr", "rrr"], {"r": (red, 1), "b": (blue, 1)})
    colors = models.main_colors(model)
    assert 1 <= len(colors) <= 3
    assert colors[0] == red  # 8 red voxels, 1 blue


def test_every_drawing_file_loads() -> None:
    names = []
    for group in MODEL_GROUPS:
        folder = data_folder() / models.DRAWINGS_FOLDER / group
        names += [file.name.removesuffix(".json") for file in folder.iterdir() if file.name.endswith(".json")]
    assert "player" in names
    assert len(names) == len(set(names))  # unique across the groups: the game names a model without its group
    parts = [f"{name}:{part}" for name in names for part in read_drawing(name)[0].get("parts", {})]
    assert any(part.startswith("avalanche:") for part in parts)  # a boss's parts, drawn in its model's file
    for name in names + parts:
        assert voxels_of(name).cells


def test_every_model_has_the_same_cubes() -> None:
    flat = {"rows": ["aa", "aa"], "palette": {"a": {"color": [1, 1, 1], "height": 1}}}
    layered = {"layers": [["aaaa"] * 4], "palette": {"a": {"color": [1, 1, 1]}}}
    assert models.parse_voxels(flat).size == models.parse_voxels(layered).size == config.MODEL_VOXEL


def test_a_scale_is_no_longer_read() -> None:
    data = {"layers": [["a"]], "palette": {"a": {"color": [1, 1, 1]}}, "scale": 2}
    with pytest.raises(models.VoxelDrawingError, match="expected the keys"):
        models.parse_voxels(data)


def test_a_model_says_the_size_it_is_meant_to_be() -> None:
    data = {"layers": [["aa", "aa", "aa"]], "palette": {"a": {"color": [1, 1, 1]}}}
    voxels = models.parse_voxels(data)
    assert models.drawing_size(data, voxels) == (2 * config.MODEL_VOXEL, 3 * config.MODEL_VOXEL)
    sized = {**data, "size": [0.1, 0.2]}
    assert models.drawing_size(sized, models.parse_voxels(sized)) == (0.1, 0.2)


@pytest.mark.parametrize("size", [[0.1], [0.1, 0], [0.1, "big"], [True, 0.1], 0.1])
def test_a_size_is_two_numbers_more_than_0(size: object) -> None:
    data = {"layers": [["a"]], "palette": {"a": {"color": [1, 1, 1]}}, "size": size}
    with pytest.raises(models.VoxelDrawingError, match="'size' must be 2 numbers"):
        models.drawing_size(data, models.parse_voxels(data))


def test_a_model_is_built_from_its_data_too() -> None:
    data = {"layers": [["a"]], "palette": {"a": {"color": [1, 1, 1]}}, "engines": [
        {"x": 0, "y": 0, "width": 1, "length": 2, "towards": "top"}
    ]}  # fmt: skip
    model = models.drawn_model("new", data)
    assert model.getName() == "new"
    assert not model.find("**/flame").isEmpty()


def test_a_drawing_gives_rows_and_a_palette_of_colors_and_heights() -> None:
    rows, palette = models.parse_drawing({"rows": ["a.", "ab"], "palette": DRAWING_PALETTE})
    assert rows == ["a.", "ab"]
    assert palette == {"a": ((1.0, 0.5, 0.0, 1.0), 3), "b": ((0.0, 0.0, 1.0, 1.0), 1)}


DRAWING_PALETTE = {"a": {"color": [1, 0.5, 0], "height": 3}, "b": {"color": [0, 0, 1], "height": 1}}


@pytest.mark.parametrize(
    ("data", "problem"),
    [
        ({"rows": ["a"]}, "expected the keys"),
        ({"rows": [], "palette": DRAWING_PALETTE}, "'rows' must be a list of strings"),
        ({"rows": ["ac"], "palette": DRAWING_PALETTE}, "not in the palette"),
        ({"rows": ["a", "ab"], "palette": DRAWING_PALETTE}, "same length"),
        ({"rows": ["a"], "palette": {"a": {"color": [1, 1], "height": 1}}}, "3 numbers from 0 to 1"),
        ({"rows": ["a"], "palette": {"a": {"color": [2, 1, 1], "height": 1}}}, "3 numbers from 0 to 1"),
        ({"rows": ["a"], "palette": {"a": {"color": [1, 1, 1], "height": 2}}}, "odd whole number"),
        ({"rows": ["a"], "palette": {"a": {"color": [1, 1, 1]}}}, "expected exactly the keys"),
        ({"rows": ["a"], "palette": {"ab": {"color": [1, 1, 1], "height": 1}}}, "one character"),
    ],
)
def test_malformed_drawings_say_what_is_wrong(data: dict[str, Any], problem: str) -> None:
    with pytest.raises(models.VoxelDrawingError, match=problem):
        models.parse_drawing(data, "broken.json")


def test_pickup_capsules_take_the_pickup_color() -> None:
    capsule = models.pickup_model("B", (1.0, 0.5, 0.0, 1))
    assert (1.0, 0.5, 0.0, 1.0) in models.main_colors(capsule)


ENGINE = {"x": 1, "y": 1, "width": 1, "length": 4, "towards": "bottom"}


def test_a_drawing_can_have_engines() -> None:
    data = {"rows": ["a.", "ab"], "palette": DRAWING_PALETTE, "engines": [ENGINE, {**ENGINE, "color": [1, 0.5, 0]}]}
    models.parse_drawing(data)  # the engines are an allowed key
    engines = models.parse_engines(data)
    assert engines[0] == models.Engine(1.0, 1.0, 1.0, 4.0, "bottom", models.FLAME_COLOR)
    assert engines[1].color == (1.0, 0.5, 0.0, 1.0)
    assert models.parse_engines({"rows": ["a"], "palette": DRAWING_PALETTE}) == []


@pytest.mark.parametrize(
    ("engine", "problem"),
    [
        ({"x": 1, "y": 1}, "expected the keys"),
        ({**ENGINE, "towards": "left"}, "'towards' must be one of"),
        ({**ENGINE, "length": 0}, "more than 0"),
        ({**ENGINE, "x": "1"}, "must be numbers"),
        ({**ENGINE, "color": [2, 0, 0]}, "3 numbers from 0 to 1"),
    ],
)
def test_malformed_engines_say_what_is_wrong(engine: dict[str, Any], problem: str) -> None:
    with pytest.raises(models.VoxelDrawingError, match=problem):
        models.parse_engines({"rows": ["a"], "palette": DRAWING_PALETTE, "engines": [engine]}, "broken.json")


def test_a_flame_leaves_the_nozzle_voxel_towards_its_side() -> None:
    rows = ["...", ".a.", "..."]  # 3 x 3: voxels of 1/3, the middle one at the origin
    size = 1 / 3
    model = NodePath("ship")
    down = models.add_flame(model, models.Engine(1, 1, 1, 2, "bottom"), (len(rows[0]), len(rows)), size)
    assert tuple(down.getPos()) == pytest.approx((0, 0, -size / 2))  # from the voxel's bottom edge
    assert down.getSz() == pytest.approx(2 * size)
    tip = model.getRelativePoint(down, Vec3(0, 0, -1))  # the flame's cards go from Z 0 to -1
    assert tip.z == pytest.approx(-size / 2 - 2 * size)
    up = models.add_flame(model, models.Engine(2, 0, 1, 1, "top"), (len(rows[0]), len(rows)), size)
    assert tuple(up.getPos()) == pytest.approx((size, 0, size * 1.5))
    assert model.getRelativePoint(up, Vec3(0, 0, -1)).z == pytest.approx(size * 2.5)


def test_ships_with_engines_have_flames() -> None:
    for name in ("player", "missile"):
        engines = model_file(name)[0]["engines"]
        assert engines
        assert len(models.model(name).findAllMatches("**/flame")) == len(engines)
    assert models.turret_model().findAllMatches("**/flame").getNumPaths() == 0  # fixed to the ground


def test_a_layered_drawing_is_real_3d_with_its_middle_layer_on_the_middle_plane() -> None:
    data = {
        "layers": [["a.", ".."], ["aa", "bb"], ["..", ".b"]],  # top (nearest the camera), middle, bottom
        "palette": {"a": {"color": RED}, "b": {"color": BLUE}},
    }
    voxels = models.parse_voxels(data, "ship.json")
    assert (voxels.width, voxels.height) == (2, 2)
    assert voxels.cells[0, 0, -1] == (1.0, 0.0, 0.0, 1.0)  # the top layer: towards the camera
    assert voxels.cells[1, 1, 1] == (0.0, 0.0, 1.0, 1.0)  # the bottom one
    assert (1, 0, -1) not in voxels.cells  # holes where it's empty: overhangs and gaps are possible
    assert len(voxels.cells) == 1 + 4 + 1


@pytest.mark.parametrize(
    ("data", "problem"),
    [
        ({"layers": [], "palette": {}}, "list of layers"),
        ({"layers": [["a"], ["aa"]], "palette": {"a": {"color": RED}}}, "same rows"),
        ({"layers": [["x"]], "palette": {"a": {"color": RED}}}, "not in the palette"),
        ({"layers": [["a"]], "palette": {"a": {"color": RED, "height": 3}}}, "exactly the key 'color'"),
    ],
)
def test_bad_layered_drawings_are_rejected(data: dict[str, Any], problem: str) -> None:
    with pytest.raises(models.VoxelDrawingError, match=problem):
        models.parse_voxels(data, "ship.json")


def test_flat_drawings_still_read_as_before() -> None:
    data = {"rows": [".a.", "aba"], "palette": {"a": {"color": RED, "height": 3}, "b": {"color": BLUE, "height": 1}}}
    voxels = models.parse_voxels(data)
    rows, palette = models.parse_drawing(data)
    assert voxels.cells == models.voxel_cells(rows, palette)
    assert (voxels.width, voxels.height) == (3, 2)


def test_an_engine_can_sit_above_the_middle_plane() -> None:
    engine = models.parse_engines(
        {"rows": ["a"], "engines": [{"x": 0, "y": 0, "width": 1, "length": 1, "towards": "top", "z": 2}]}, "ship.json"
    )[0]
    assert engine.z == 2.0
    flame = models.add_flame(NodePath("ship"), engine, (1, 1), 0.5)
    assert flame.getY() == pytest.approx(-1.0)  # towards the camera (-Y)


def test_a_quad_splits_along_its_brighter_diagonal() -> None:
    corners = (Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(1, 0, 1), Vec3(0, 0, 1))
    for brightness, diagonal in (((0.5, 1, 0.5, 1), (1, 3)), ((1, 0.5, 1, 0.5), (0, 2))):
        mesh = models.MeshBuilder()
        mesh.quad(*corners, (1, 1, 1, 1), Vec3(0, 1, 0), brightness)
        triangles = triangles_of(mesh.build("quad"))
        shared = set.intersection(*({tuple(round(v, 6) for v in point) for point in points} for points, _ in triangles))
        assert shared == {tuple(corners[index]) for index in diagonal}


def test_an_empty_mesh_builds_an_empty_node() -> None:
    mesh = models.MeshBuilder()
    mesh.cells({}, 1.0, Vec3(0, 0, 0))
    assert mesh.build("nothing").getGeom(0).getVertexData().getNumRows() == 0


def test_main_colors_skip_see_through_parts_and_look_under_empty_nodes() -> None:
    holder = NodePath("holder")
    models.shield_bubble_model().reparentTo(holder)  # all see-through
    assert models.main_colors(holder) == ((1.0, 1.0, 1.0, 1.0),)  # nothing solid: white
    models.model("drone").reparentTo(holder)
    assert models.main_colors(holder) == models.main_colors(models.model("drone"))


@pytest.mark.parametrize(
    ("data", "problem"),
    [
        ({"layers": [["a"]], "palette": ["a"]}, "map characters to a color"),
        ({"rows": ["a"], "palette": ["a"]}, "map characters to a color and a height"),
        ({"rows": ["a"], "palette": {"a": {"color": RED, "height": 1}}, "engines": {}}, "must be a list"),
    ],
)
def test_palettes_and_engines_of_the_wrong_kind_are_refused(data: dict[str, Any], problem: str) -> None:
    with pytest.raises(models.VoxelDrawingError, match=problem):
        read_model(data)


def read_model(data: dict[str, Any]) -> None:
    """Read a model file: its cubes, then its engines."""
    models.parse_voxels(data, "ship.json")
    models.parse_engines(data, "ship.json")


def test_an_engine_height_must_be_a_number() -> None:
    engine = {"x": 0, "y": 0, "width": 1, "length": 1, "towards": "top", "z": "up"}
    with pytest.raises(models.VoxelDrawingError, match="'z' must be a number"):
        models.parse_engines({"rows": ["a"], "engines": [engine]}, "ship.json")
