from pewpy.generators.levels.worlds.highlands import HIGHLANDS
from tests.generators.levels.worlds.plans import assert_playable


def test_its_levels_can_be_played() -> None:
    assert_playable(HIGHLANDS)


def test_its_levels_have_names_of_their_own() -> None:
    names = [level.name for level in HIGHLANDS.levels]
    assert len(set(names)) == len(names)
