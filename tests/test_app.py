import pytest

from pewpy.app import FLAME_FLICKER, GAME_ASPECT, flame_scale, letterbox


def region_shape(window_width: int, window_height: int) -> float:
    left, right, bottom, top = letterbox(window_width, window_height)
    return (right - left) * window_width / ((top - bottom) * window_height)


@pytest.mark.parametrize(
    ("width", "height"), [(1280, 1024), (675, 900), (1200, 700), (600, 1000), (1920, 1080), (300, 2000)]
)
def test_the_game_area_keeps_its_shape_in_any_window(width, height):
    assert region_shape(width, height) == pytest.approx(GAME_ASPECT)


def test_a_wide_window_gets_bars_on_the_sides():
    left, right, bottom, top = letterbox(1600, 900)
    assert (bottom, top) == (0.0, 1.0)
    assert left == pytest.approx(1 - right)  # centered
    assert left > 0


def test_a_tall_window_gets_bars_at_the_top_and_bottom():
    left, right, bottom, top = letterbox(600, 1000)
    assert (left, right) == (0.0, 1.0)
    assert bottom == pytest.approx(1 - top)
    assert bottom > 0


def test_a_window_of_the_game_shape_has_no_bars():
    assert letterbox(1280, 1024) == pytest.approx((0.0, 1.0, 0.0, 1.0))


def test_engine_flames_waver_and_grow_with_thrust():
    lengths = [flame_scale(time / 10, 0.0) for time in range(50)]
    assert min(lengths) < 1 < max(lengths)
    assert max(lengths) - min(lengths) <= 2 * sum(FLAME_FLICKER) + 1e-9
    assert flame_scale(0.0, 0.0, thrust=1.0) > flame_scale(0.0, 0.0) > flame_scale(0.0, 0.0, thrust=-1.0)
