import pytest
from panda3d.core import NodePath, Vec3

from pewpy.graphics.models.drawings.engines import Engine
from pewpy.graphics.models.flames import FLAME_CORE_COLOR, add_flame


def test_a_flame_leaves_the_nozzle_voxel_towards_its_side() -> None:
    rows = ["...", ".a.", "..."]  # 3 x 3: voxels of 1/3, the middle one at the origin
    size = 1 / 3
    model = NodePath("ship")
    down = add_flame(model, Engine(1, 1, 1, 2, "bottom"), (len(rows[0]), len(rows)), size)
    assert tuple(down.getPos()) == pytest.approx((0, 0, -size / 2))  # from the voxel's bottom edge
    assert down.getSz() == pytest.approx(2 * size)
    tip = model.getRelativePoint(down, Vec3(0, 0, -1))  # the flame's cards go from Z 0 to -1
    assert tip.z == pytest.approx(-size / 2 - 2 * size)
    up = add_flame(model, Engine(2, 0, 1, 1, "top"), (len(rows[0]), len(rows)), size)
    assert tuple(up.getPos()) == pytest.approx((size, 0, size * 1.5))
    assert model.getRelativePoint(up, Vec3(0, 0, -1)).z == pytest.approx(size * 2.5)


def test_an_engine_above_the_middle_plane_has_its_flame_towards_the_camera() -> None:
    flame = add_flame(NodePath("ship"), Engine(0, 0, 1, 1, "top", z=2.0), (1, 1), 0.5)
    assert flame.getY() == pytest.approx(-1.0)  # towards the camera (-Y)


def test_a_flame_is_a_glow_of_its_engines_color_round_a_white_hot_core() -> None:
    flame = add_flame(NodePath("ship"), Engine(0, 0, 1, 1, "top", color=(1.0, 0.5, 0.0, 1.0)), (1, 1), 0.5)
    glow, core = flame.find("glow"), flame.find("core")
    assert tuple(glow.getColor()) == pytest.approx((1.0, 0.5, 0.0, 1.0), abs=1e-3)  # colors are stored compactly
    assert tuple(core.getColor()) == pytest.approx(FLAME_CORE_COLOR, abs=1e-3)
    assert glow.getNumChildren() == core.getNumChildren() == 2  # crossed cards
