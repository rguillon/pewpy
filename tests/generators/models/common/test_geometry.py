import pytest

from pewpy.generators.models.common.geometry import inside, miss

SQUARE = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]


def test_sizes_miss_nothing_when_they_are_the_ones_wanted() -> None:
    assert miss((3.0, 4.0), (3.0, 4.0)) == 0.0


def test_a_size_twice_too_big_misses_as_much_as_one_half_too_small() -> None:
    assert miss((8.0,), (4.0,)) == pytest.approx(miss((2.0,), (4.0,)))
    assert miss((8.0, 4.0), (4.0, 4.0)) < miss((8.0, 8.0), (4.0, 4.0))


def test_tiny_sizes_count_as_half_a_cube() -> None:
    assert miss((0.1,), (0.5,)) == 0.0


@pytest.mark.parametrize(("x", "y", "within"), [(1.0, 1.0, True), (3.0, 1.0, False), (1.0, -0.5, False)])
def test_a_point_is_inside_a_polygon_or_not(x: float, y: float, within: bool) -> None:
    assert inside(x, y, SQUARE) is within


def test_a_point_in_a_hollow_of_a_polygon_is_outside() -> None:
    u_shape = [(0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (2.0, 3.0), (2.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0)]
    assert not inside(1.5, 2.0, u_shape)
    assert inside(0.5, 2.0, u_shape)
