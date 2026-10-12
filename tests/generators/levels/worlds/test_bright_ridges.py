from pewpy.generators.levels.worlds.bright_ridges import BRIGHT_RIDGES
from tests.generators.levels.worlds.plans import assert_playable


def test_its_levels_can_be_played() -> None:
    assert_playable(BRIGHT_RIDGES)


def test_its_levels_have_names_of_their_own() -> None:
    names = [level.name for level in BRIGHT_RIDGES.levels]
    assert len(set(names)) == len(names)
