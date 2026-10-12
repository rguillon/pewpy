import pytest

from pewpy.graphics.models.built.laser_beam import laser_beam_model
from pewpy.graphics.models.colors import main_colors
from tests.graphics.models.meshes import all_points


def test_a_laser_beam_is_a_thin_unlit_box_a_beam_long() -> None:
    beam = laser_beam_model((1.0, 0.0, 0.0, 1.0))
    points = all_points(beam)
    assert max(point.z for point in points) - min(point.z for point in points) == pytest.approx(1.0)
    assert max(point.x for point in points) - min(point.x for point in points) == pytest.approx(0.25)
    assert beam.hasLightOff()
    assert beam.hasTransparency()
    assert main_colors(beam) == ((1.0, 0.0, 0.0, 1.0),)
