import pytest

from pewpy.scenery import params
from pewpy.scenery.background.stars import Starfield
from tests.scenery.background.views import AREA


def space_stars() -> params.Stars:
    stars = params.resolve("space").stars
    assert stars is not None
    return stars


STARS = space_stars()


def test_star_layers_scroll_down_with_parallax() -> None:
    starfield = Starfield(STARS, seed=0, area=AREA)
    starfield.update(0.1, scroll_speed=0.2)
    for layer in starfield.layers:
        assert layer.offset == pytest.approx(0.2 * layer.speed_factor * 0.1)
    assert len({layer.speed_factor for layer in starfield.layers}) > 1


def test_star_layers_wrap_after_one_area_height() -> None:
    starfield = Starfield(STARS, seed=0, area=AREA)
    layer = starfield.layers[-1]
    starfield.update(AREA.height / layer.speed_factor + 0.5, scroll_speed=1.0)
    assert layer.offset == pytest.approx(0.5 * layer.speed_factor)


def test_stars_fill_the_area_and_stay_still_without_scrolling() -> None:
    starfield = Starfield(STARS, seed=0, area=AREA)
    stars = [star for layer in starfield.layers for star in layer.stars]
    assert all(AREA.left <= x <= AREA.right and AREA.bottom <= y <= AREA.top for x, y in stars)
    starfield.update(1.0, scroll_speed=0.0)
    assert all(layer.offset == 0 for layer in starfield.layers)


def test_a_starfield_has_as_many_stars_as_asked_the_same_for_the_same_seed() -> None:
    first, second = Starfield(STARS, AREA, count=90, seed=4), Starfield(STARS, AREA, count=90, seed=4)
    assert sum(len(layer.stars) for layer in first.layers) == pytest.approx(90, abs=len(first.layers))
    assert [layer.stars for layer in first.layers] == [layer.stars for layer in second.layers]
