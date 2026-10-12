from pewpy.generators.levels.worlds.wildwood import WILDWOOD
from tests.generators.levels.worlds.plans import assert_playable


def test_its_levels_can_be_played() -> None:
    assert_playable(WILDWOOD)


def test_its_levels_have_names_of_their_own() -> None:
    names = [level.name for level in WILDWOOD.levels]
    assert len(set(names)) == len(names)
