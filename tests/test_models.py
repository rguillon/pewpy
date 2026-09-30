import math
from functools import partial
from importlib import resources

import numpy as np
import pytest
from panda3d.core import GeomNode, GeomVertexReader, NodePath, Vec3

from pewpy import app, config, ground_look, models

SHIP_MODELS = [
    models.player_model,
    models.drone_model,
    models.weaver_model,
    models.diver_model,
    models.gunship_model,
    models.turret_model,
    models.swarmer_model,
    models.sniper_model,
    models.mine_layer_model,
    models.mine_model,
    models.shield_carrier_model,
    models.splitter_model,
    models.missile_model,
    models.repair_model,
    lambda: models.pickup_model("B", (1, 1, 0, 1)),
]


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


def zeros(heights: list[list[int]]) -> list[list[int]]:
    """Kinds for a ground that doesn't use them."""
    return [[0] * len(line) for line in heights]


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


def test_cube_faces_outward():
    cube = models.make_cube()
    triangles = triangles_of(cube)
    assert len(triangles) == 12
    for corners, normal in triangles:
        winding = (corners[1] - corners[0]).cross(corners[2] - corners[0])
        assert winding.dot(normal) > 0  # counter-clockwise seen from outside
        center = (corners[0] + corners[1] + corners[2]) / 3
        assert normal.dot(center) > 0  # and pointing away from the cube's center


def test_ellipsoid_faces_away_from_its_center():
    mesh = models.MeshBuilder()
    center = Vec3(0.1, 0.2, 0.3)
    mesh.ellipsoid(center, Vec3(0.1, 0.2, 0.3), (1, 1, 1, 1))
    for corners, normal in triangles_of(mesh.build("shapes")):
        assert normal.dot((corners[0] + corners[1] + corners[2]) / 3 - center) > 0


WHITE = (1.0, 1.0, 1.0, 1.0)


def test_touching_voxels_hide_their_shared_faces():
    mesh = models.MeshBuilder()
    mesh.voxels(["xx"], {"x": (WHITE, 1)}, 1.0)
    triangles = triangles_of(mesh.build("pair"))
    assert len(triangles) == 2 * 6  # a 2 x 1 x 1 box: the shared faces are hidden, the flat sides merged
    for corners, normal in triangles:
        winding = (corners[1] - corners[0]).cross(corners[2] - corners[0])
        assert winding.dot(normal) > 0
        assert normal.dot((corners[0] + corners[1] + corners[2]) / 3) > 0  # outward from the pair's center


def test_lone_voxel_is_not_darkened():
    mesh = models.MeshBuilder()
    mesh.voxels(["x"], {"x": (WHITE, 1)}, 1.0)
    assert {color for triangle in mesh.triangles for _, color, _ in triangle} == {WHITE}


def test_voxel_corners_next_to_other_voxels_are_darkened():
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
def test_occlusion_counts_the_voxels_in_front_of_a_corner(side_a, side_b, corner, expected):
    level = models.occlusion_level(np.array([side_a]), np.array([side_b]), np.array([corner]))
    assert models.OCCLUSION_BRIGHTNESS[level[0]] == expected


def test_flat_runs_of_alike_faces_become_one_rectangle_counting_its_cubes():
    mesh = models.MeshBuilder()
    mesh.voxels(["xxx", "xxx"], {"x": (WHITE, 1)}, 1.0)  # a 3 x 2 plate, one cube thick
    assert len(mesh.triangles) == 2 * 6  # still a box: one rectangle per side
    uvs = {uv for triangle in mesh.triangles for _, _, uv in triangle}
    assert (3.0, 2.0) in uvs  # the front: 3 cubes across, 2 up, so the shader bevels each cube


def test_merged_faces_cover_exactly_the_faces_of_the_cubes():
    """Merging changes the triangles, not the surface: per direction, the area is the number of visible cube faces."""
    for build in (models.player_model, models.gunship_model, models.drone_model):
        node = build().node()
        assert isinstance(node, GeomNode)
        area: dict[tuple[int, int, int], float] = {}
        for corners, normal in triangles_of(node):
            key = (round(normal.x), round(normal.y), round(normal.z))
            area[key] = area.get(key, 0.0) + (corners[1] - corners[0]).cross(corners[2] - corners[0]).length() / 2
        rows, palette = models.load_drawing(build.__name__.removesuffix("_model"))
        cells = models.voxel_cells(rows, palette)
        voxel = config.MODEL_VOXEL
        for direction in models.FACE_DIRECTIONS:
            dx, dy, dz = direction
            visible = sum((column + dx, row - dz, layer + dy) not in cells for column, row, layer in cells)
            assert area.get(direction, 0.0) == pytest.approx(visible * voxel * voxel, rel=1e-4)


def test_faces_only_merge_where_their_shading_stays_the_same():
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


def test_only_voxel_faces_get_bevel_coordinates():
    voxels = models.MeshBuilder()
    voxels.voxels(["x"], {"x": (WHITE, 1)}, 1.0)
    assert {uv for triangle in voxels.triangles for _, _, uv in triangle} == set(models.QUAD_UVS)  # one cube
    box = models.MeshBuilder()
    box.box(Vec3(0, 0, 0), Vec3(1, 1, 1), WHITE)
    assert {uv for triangle in box.triangles for _, _, uv in triangle} == {models.NO_BEVEL}
    assert models.make_cube().getGeom(0).getVertexData().hasColumn("texcoord")


def test_ground_columns_rise_towards_the_camera():
    cells = models.ground_cells([[0, 2]], first_row=5)
    assert set(cells) == {(0, 5, 0), (1, 5, 0), (1, 5, -1), (1, 5, -2)}


def test_buried_ground_voxels_are_not_drawn_but_still_hide_faces():
    # A 3 x 3 plateau of height 2 is a 3 x 3 x 3 block: only its very middle voxel is buried on every side.
    plateau = [[2, 2, 2], [2, 2, 2], [2, 2, 2]]
    cells = models.ground_cells(plateau, 0, max_height=2)
    buried = [cell for cell in cells if models.buried(cell, frozenset(cells))]
    assert buried == [(1, 1, -1)]
    # Same outside as drawing every voxel: 5 faces of 3 x 3 on the outside (the back one too), 2 triangles each.
    points = all_points(ground_look.ground_chunk_model("planet", plateau, zeros(plateau), 1.0, [], [], max_height=2))
    assert len(points) == (4 * 3 * 3 + 3 * 3 + 3 * 3) * 2 * 3


def test_city_cells_light_some_windows_and_one_beacon_per_tower():
    heights = [[0, 0, 0, 0], [0, 6, 6, 2], [0, 6, 6, 2]]
    lots = [[0, 0, 0, 0], [0, 1, 1, 2], [0, 1, 1, 2]]
    cells, glowing = models.city_cells(heights, lots, max_height=6)
    assert glowing <= set(cells)
    beacons = [cell for cell in glowing if cells[cell] == models.BEACON_COLOR]
    assert beacons == [(1, 1, -6)]  # the tower's corner; the low building gets none
    assert (1, 1, -7) not in cells or cells[(1, 1, -7)] != models.BEACON_COLOR
    windows = {cell for cell in glowing if cells[cell] in models.WINDOW_COLORS}
    assert all(-cell[2] % 2 == 1 for cell in windows)  # windows only on odd floors


def test_city_lights_are_not_pink_like_enemy_bullets():
    for color in (*models.WINDOW_COLORS, models.STREET_LIGHT_COLOR, models.BEACON_COLOR):
        red, green, blue, _ = color
        assert not (red > 0.3 and blue > 0.3 and green < red)  # pink / magenta


def test_islands_rise_from_the_water_in_colored_bands():
    cells = models.island_cells([[0, 1, 4]], max_height=4)
    assert (0, 0, 0) not in cells and (0, 0, -1) not in cells  # water: no voxel
    assert set(cells) == {(1, 0, -1), (2, 0, -1), (2, 0, -2), (2, 0, -3), (2, 0, -4)}
    beach, peak = models.ISLAND_COLORS[0][1], models.ISLAND_COLORS[-1][1]
    assert cells[(1, 0, -1)] != cells[(2, 0, -4)]
    assert max(cells[(1, 0, -1)][:3]) <= max(beach[:3]) * 1.2
    assert max(cells[(2, 0, -4)][:3]) <= max(peak[:3]) * 1.2


def test_the_sea_is_a_water_surface_facing_the_camera():
    shallows = [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]  # two rows of the strip, plus the next strip's first
    node = ground_look.ground_chunk_model(
        "ocean", [[0, 0], [0, 0]], zeros([[0, 0], [0, 0]]), 1.0, [0, 0], [0, 0], 3, shallows
    )
    geom_node = node.node()
    assert isinstance(geom_node, GeomNode)
    triangles = triangles_of(geom_node)
    assert triangles
    for _, normal in triangles:
        assert normal.y == pytest.approx(-1.0)  # towards the camera
    mesh = models.MeshBuilder()
    models.water_surface(mesh, shallows, 1.0, 2)
    assert {uv for triangle in mesh.triangles for _, _, uv in triangle} == {models.WATER_UV}
    brightness = {color[2] for triangle in mesh.triangles for _, color, _ in triangle}
    assert max(brightness) > min(brightness)  # lighter in the shallows


def test_glowing_voxel_faces_are_marked_for_the_shader():
    mesh = models.MeshBuilder()
    mesh.cells({(0, 0, 0): WHITE, (1, 0, 0): WHITE}, 1.0, Vec3(0, 0, 0), glowing=frozenset({(1, 0, 0)}))
    uvs = {uv for triangle in mesh.triangles for _, _, uv in triangle}
    assert uvs == set(models.QUAD_UVS) | set(models.GLOW_UVS)


def test_ground_strips_have_no_faces_at_the_seams():
    flat = [[1, 1], [1, 1]]
    alone = all_points(ground_look.ground_chunk_model("planet", flat, zeros(flat), 1.0, [], [], 3))
    joined = all_points(ground_look.ground_chunk_model("planet", flat, zeros(flat), 1.0, [1, 1], [1, 1], 3))
    # The neighboring strips hide the faces along the top and bottom edges (2 columns x 2 layers each),
    # 2 triangles of 3 points per face.
    assert len(alone) - len(joined) == 2 * (2 * 2) * 2 * 3


@pytest.mark.parametrize(
    "build", [models.distant_planet_model, *(partial(models.rock_model, shape) for shape in range(3))]
)
def test_background_models_fit_the_unit_box(build):
    points = all_points(build())
    for axis in range(3):
        assert min(point[axis] for point in points) >= -0.5 - 1e-6
        assert max(point[axis] for point in points) <= 0.5 + 1e-6


def test_rocks_differ_by_shape_and_repeat_for_the_same_shape():
    assert all_points(models.rock_model(1)) == all_points(models.rock_model(1))
    assert all_points(models.rock_model(1)) != all_points(models.rock_model(2))


def test_voxel_thickness_is_centered_on_the_depth():
    cells = models.voxel_cells(["a", "b"], {"a": (WHITE, 1), "b": (WHITE, 5)})
    assert sorted(layer for column, row, layer in cells if row == 1) == [-2, -1, 0, 1, 2]
    assert [layer for column, row, layer in cells if row == 0] == [0]


@pytest.mark.parametrize(
    ("rows", "palette"), [(["ab", "a"], {"a": (WHITE, 1), "b": (WHITE, 1)}), (["a"], {"a": (WHITE, 2)})]
)
def test_bad_voxel_drawings_are_rejected(rows, palette):
    with pytest.raises(ValueError, match="must"):
        models.voxel_cells(rows, palette)


@pytest.mark.parametrize("build", SHIP_MODELS, ids=lambda build: build.__name__)
def test_ship_models_are_more_than_a_cube(build):
    assert len(all_points(build())) > 3 * 12


@pytest.mark.parametrize(("kind", "function"), list(app.SHIP_MODELS.items()), ids=lambda item: str(item))
def test_ship_models_are_about_the_size_of_their_hitbox(kind, function):
    """Every cube is config.MODEL_VOXEL (the Swarmer's): a model's drawing gives its size, which must fit its
    hitbox."""
    entity = kind()
    points = all_points(getattr(models, function)())
    width = max(point.x for point in points) - min(point.x for point in points)
    height = max(point.z for point in points) - min(point.z for point in points)
    assert width == pytest.approx(entity.width, rel=0.2)
    assert height <= entity.height * 1.2
    assert max(width, height) == pytest.approx(max(entity.width, entity.height), rel=0.2)


def test_every_drawing_has_the_same_cubes():
    """Models aren't stretched: a drawing's voxel is config.MODEL_VOXEL, whatever its size."""
    for build in (models.swarmer_model, models.player_model, models.gunship_model):
        points = all_points(build())
        xs = sorted({round(point.x / config.MODEL_VOXEL, 3) for point in points})
        assert all(abs(x - round(x * 2) / 2) < 1e-3 for x in xs)  # corners on the half-voxel grid


def test_turret_has_a_barrel_to_aim():
    assert not models.turret_model().find("**/barrel").isEmpty()


@pytest.mark.parametrize(("dx", "dz"), [(0, -1), (1, 0), (-1, 0), (0, 1), (1, -1), (-0.3, 0.7)])
def test_facing_roll_points_the_model_along_the_direction(dx, dz):
    root = NodePath("root")
    model = root.attachNewNode("model")
    model.setR(models.facing_roll(dx, dz))
    front = root.getRelativeVector(model, Vec3(0, 0, -1))  # models point down the screen
    length = math.hypot(dx, dz)
    assert front.x == pytest.approx(dx / length, abs=1e-5)
    assert front.z == pytest.approx(dz / length, abs=1e-5)


def test_main_colors_are_what_most_of_a_model_is_made_of():
    red, blue = (1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0)
    model = models.voxel_model("test", ["rrr", "rbr", "rrr"], {"r": (red, 1), "b": (blue, 1)})
    colors = models.main_colors(model)
    assert 1 <= len(colors) <= 3
    assert colors[0] == red  # 8 red voxels, 1 blue


def test_every_drawing_file_loads():
    folder = resources.files("pewpy") / models.DRAWINGS_FOLDER
    names = sorted(file.name.removesuffix(".json") for file in folder.iterdir() if file.name.endswith(".json"))
    assert "player" in names
    for name in names:
        rows, palette = models.load_drawing(name)
        assert models.voxel_cells(rows, palette)


def test_a_drawing_gives_rows_and_a_palette_of_colors_and_heights():
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
def test_malformed_drawings_say_what_is_wrong(data, problem):
    with pytest.raises(models.VoxelDrawingError, match=problem):
        models.parse_drawing(data, "broken.json")


def test_pickup_capsules_take_the_pickup_color():
    capsule = models.pickup_model("B", (1.0, 0.5, 0.0, 1))
    assert (1.0, 0.5, 0.0, 1.0) in models.main_colors(capsule)


ENGINE = {"x": 1, "y": 1, "width": 1, "length": 4, "towards": "bottom"}


def test_a_drawing_can_have_engines():
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
def test_malformed_engines_say_what_is_wrong(engine, problem):
    with pytest.raises(models.VoxelDrawingError, match=problem):
        models.parse_engines({"rows": ["a"], "palette": DRAWING_PALETTE, "engines": [engine]}, "broken.json")


def test_a_flame_leaves_the_nozzle_voxel_towards_its_side():
    rows = ["...", ".a.", "..."]  # 3 x 3: voxels of 1/3, the middle one at the origin
    size = 1 / 3
    model = NodePath("ship")
    down = models.add_flame(model, models.Engine(1, 1, 1, 2, "bottom"), rows, size)
    assert tuple(down.getPos()) == pytest.approx((0, 0, -size / 2))  # from the voxel's bottom edge
    assert down.getSz() == pytest.approx(2 * size)
    tip = model.getRelativePoint(down, Vec3(0, 0, -1))  # the flame's cards go from Z 0 to -1
    assert tip.z == pytest.approx(-size / 2 - 2 * size)
    up = models.add_flame(model, models.Engine(2, 0, 1, 1, "top"), rows, size)
    assert tuple(up.getPos()) == pytest.approx((size, 0, size * 1.5))
    assert model.getRelativePoint(up, Vec3(0, 0, -1)).z == pytest.approx(size * 2.5)


def test_ships_with_engines_have_flames():
    assert len(models.player_model().findAllMatches("**/flame")) == 2
    assert len(models.missile_model().findAllMatches("**/flame")) == 1
    assert models.turret_model().findAllMatches("**/flame").getNumPaths() == 0  # fixed to the ground


def test_every_model_candidate_loads_and_builds_with_its_engines():
    names = models.candidate_names()  # however many tools/make_candidates.py wrote
    assert names
    assert names[0] == "candidates/001"
    for name in names:
        rows, palette = models.load_drawing(name)
        assert models.voxel_cells(rows, palette)
        engines = models.load_engines(name)
        assert engines  # every candidate flies
        assert all(engine.towards == "top" for engine in engines)  # enemies point down: flames at the back
        assert models.drawing_model(name).findAllMatches("**/flame").getNumPaths() == len(engines)
