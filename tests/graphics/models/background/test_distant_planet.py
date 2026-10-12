from panda3d.core import GeomNode

from pewpy.graphics.models.background.distant_planet import distant_planet_model
from pewpy.graphics.models.colors import main_colors
from tests.graphics.models.meshes import all_points, assert_closed_and_facing_out

PLANET = ((0.16, 0.15, 0.15, 1.0), (0.2, 0.18, 0.16, 1.0))


def test_the_distant_planet_fits_the_unit_box() -> None:
    points = all_points(distant_planet_model(PLANET))
    for axis in range(3):
        assert min(point[axis] for point in points) >= -0.5 - 1e-6
        assert max(point[axis] for point in points) <= 0.5 + 1e-6


def test_the_distant_planet_is_a_closed_surface_facing_out() -> None:
    node = distant_planet_model(((0.2, 0.2, 0.2, 1.0),)).node()
    assert isinstance(node, GeomNode)
    assert_closed_and_facing_out(node)


def test_the_planet_is_banded_in_its_colors() -> None:
    assert len(main_colors(distant_planet_model(((1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0)), seed=3))) > 1
