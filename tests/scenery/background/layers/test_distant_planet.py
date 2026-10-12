import random

from pewpy.scenery import params
from pewpy.scenery.background.layers.distant_planet import planet_layer
from tests.scenery.background.views import AREA


def test_one_planet_high_on_the_left_or_the_right_turning() -> None:
    planet = params.resolve("space").planet
    assert planet is not None
    sides = set()
    for seed in range(10):
        layer = planet_layer(random.Random(seed), planet, AREA)
        (drifter,) = layer.drifters
        assert (layer.kind, layer.depth) == ("planet", planet.depth)
        assert drifter.y == AREA.top - AREA.height * 0.25
        assert planet.size[0] <= drifter.size <= planet.size[1]
        assert drifter.spin == (planet.spin, 0.0, 0.0)
        sides.add(drifter.x < 0)
    assert sides == {True, False}
