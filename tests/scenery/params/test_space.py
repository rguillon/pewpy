import dataclasses
from itertools import pairwise

import pytest

from pewpy.scenery.params.presets import resolve
from pewpy.scenery.params.space import DistantPlanet, Nebulas, StarLayer, Stars


def test_space_has_stars_nebulas_and_a_planet() -> None:
    space = resolve("space")
    assert isinstance(space.stars, Stars)
    assert isinstance(space.nebulas, Nebulas)
    assert isinstance(space.planet, DistantPlanet)


def test_far_stars_are_slow_small_and_dim() -> None:
    stars = resolve("space").stars
    assert stars is not None
    layers = stars.layers
    assert all(isinstance(layer, StarLayer) for layer in layers)
    for far, near in pairwise(layers):
        assert far.speed < near.speed
        assert far.size < near.size
        assert far.brightness < near.brightness


def test_the_planet_is_far_slow_and_banded_in_palettes_of_colors() -> None:
    planet = resolve("space").planet
    assert planet is not None
    assert planet.depth > 1.0
    assert planet.size[0] < planet.size[1]
    assert all(len(color) == 3 for palette in planet.palettes for color in palette)
    with pytest.raises(dataclasses.FrozenInstanceError):
        planet.spin = 0.0  # ty: ignore[invalid-assignment]
