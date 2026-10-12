import random

import pytest

from pewpy.scenery.background.drift import Drifter, DriftLayer
from tests.scenery.background.views import AREA


def test_drifters_move_spin_and_come_back_above_the_top() -> None:
    rock = Drifter(0.0, AREA.bottom - 0.09, size=0.1, speed_factor=0.5, spin=(10.0, 0.0, -20.0))
    layer = DriftLayer("planet", 1.0, AREA, [rock])
    layer.update(0.5, scroll_speed=0.2)
    assert rock.angle == pytest.approx((5.0, 0.0, -10.0))
    assert AREA.top - 0.2 < rock.y <= AREA.top + rock.size
    assert AREA.left <= rock.x <= AREA.right


def test_a_drifter_still_in_the_area_keeps_its_column() -> None:
    cloud = Drifter(0.3, 0.5, size=0.1, speed_factor=1.0)
    DriftLayer("cloud", 1.0, AREA, [cloud], random.Random(0)).update(1.0, scroll_speed=0.2)
    assert (cloud.x, cloud.y) == (0.3, pytest.approx(0.3))


def test_wind_blows_clouds_around_the_sides() -> None:
    cloud = Drifter(AREA.right + 0.05, 0.0, size=0.1, speed_factor=0.0, wind=0.1)
    layer = DriftLayer("mist", 0.1, AREA, [cloud])
    layer.update(1.0, scroll_speed=0.0)
    assert AREA.left - cloud.size <= cloud.x < AREA.left + 0.1  # gone off the right, back on the left


def test_a_drifter_blown_off_the_left_comes_back_on_the_right() -> None:
    cloud = Drifter(AREA.left - 0.05, 0.0, size=0.1, speed_factor=0.0, wind=-0.1)
    DriftLayer("mist", 0.1, AREA, [cloud]).update(1.0, scroll_speed=0.0)
    assert AREA.right - 0.1 < cloud.x <= AREA.right + cloud.size
