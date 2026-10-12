import random

import pytest

from pewpy.generators.backgrounds.themes import THEMES, between, haze, palette, vary, water
from pewpy.scenery import params


def test_every_theme_starts_from_a_new_kind_of_ground() -> None:
    assert {theme.preset for theme in THEMES.values()} == {"salt_pan", "savanna", "badlands"}
    for theme in THEMES.values():
        assert theme.adjectives
        assert theme.nouns
        assert set(theme.times) <= set(params.resolve(theme.preset).times_of_day)
        assert 0 <= theme.clouds[0] <= theme.clouds[1] <= 1


@pytest.mark.parametrize("name", list(THEMES))
def test_every_themes_changes_are_a_scenery_the_game_reads(name: str) -> None:
    theme = THEMES[name]
    params.resolve(theme.preset, theme.changes(random.Random(0)))


def test_a_color_varies_a_little_and_never_past_full() -> None:
    rng = random.Random(1)
    for _ in range(50):
        red, green, blue = vary(rng, [0.5, 0.2, 1.0])
        assert 0.46 <= red <= 0.54
        assert 0.184 <= green <= 0.216
        assert blue <= 1.0


def test_a_palette_varies_each_of_its_colors() -> None:
    varied = palette(random.Random(1), {"a": [0.5, 0.5, 0.5], "b": [0.2, 0.2, 0.2]})
    assert set(varied) == {"a", "b"}
    assert varied["a"] != [0.5, 0.5, 0.5]


def test_numbers_water_and_haze_are_drawn_within_their_ranges() -> None:
    rng = random.Random(2)
    assert all(0.1 <= between(rng, 0.1, 0.2) <= 0.2 for _ in range(20))
    sea = water(rng, [0.1, 0.1, 0.2], [0.2, 0.2, 0.3])
    assert sea["kind"] == "water"
    assert set(sea["colors"]) == {"deep", "shallow", "foam"}
    air = haze(rng, [0.5, 0.5, 0.5], 0.3, 0.4)
    assert 0.3 <= air["amount"] <= 0.4
