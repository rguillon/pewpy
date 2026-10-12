from pewpy.generators.levels.worlds.ironworks import IRONWORKS
from tests.generators.levels.worlds.plans import assert_playable


def test_its_levels_can_be_played() -> None:
    assert_playable(IRONWORKS)


def test_its_levels_have_names_of_their_own() -> None:
    names = [level.name for level in IRONWORKS.levels]
    assert len(set(names)) == len(names)
