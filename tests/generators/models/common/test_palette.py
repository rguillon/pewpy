import random

from pewpy.generators.models.common.palette import (
    ACCENTS,
    COCKPIT,
    GREYS,
    HULL_TINTS,
    LIVERIES,
    PLAYER_TINT,
    UNDERSIDE,
    Colors,
    palette,
    pick_colors,
    pick_player_colors,
)


def test_colors_are_picked_among_the_tints_accents_and_liveries() -> None:
    colors = pick_colors(random.Random(3))
    assert colors.tint in HULL_TINTS.values()
    assert colors.accent in ACCENTS
    assert colors.livery in LIVERIES


def test_a_players_ship_is_always_bluish() -> None:
    assert all(pick_player_colors(random.Random(seed)).tint == PLAYER_TINT for seed in range(10))


def test_a_palette_tints_its_greys_and_shares_the_rest() -> None:
    white = palette(GREYS, Colors((1.0, 1.0, 1.0), "red", LIVERIES[0]))
    dark = palette(GREYS, Colors((0.5, 0.5, 0.5), "red", LIVERIES[0]))
    assert set(GREYS) < set(white)
    hull = next(iter(GREYS))
    assert dark[hull]["color"] == [round(channel * 0.5, 3) for channel in white[hull]["color"]]
    assert white["c"]["color"] == list(COCKPIT) == dark["c"]["color"]
    assert white["p"]["color"] == list(ACCENTS["red"][0])
    assert white["L"]["color"] == list(LIVERIES[0])


def test_the_underside_is_the_hull_darker() -> None:
    colors = palette(GREYS, Colors((1.0, 1.0, 1.0), "red", LIVERIES[0]))
    assert colors["D"]["color"] == [round(min(1.0, channel * UNDERSIDE), 3) for channel in colors["h"]["color"]]
