from pewpy.generators.levels.worlds.lush_veld import LUSH_VELD
from tests.generators.levels.worlds.plans import assert_playable


def test_its_levels_can_be_played() -> None:
    assert_playable(LUSH_VELD)


def test_its_levels_have_names_of_their_own() -> None:
    names = [level.name for level in LUSH_VELD.levels]
    assert len(set(names)) == len(names)
