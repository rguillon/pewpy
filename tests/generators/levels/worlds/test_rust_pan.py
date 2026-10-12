from pewpy.generators.levels.worlds.rust_pan import RUST_PAN
from tests.generators.levels.worlds.plans import assert_playable


def test_its_levels_can_be_played() -> None:
    assert_playable(RUST_PAN)


def test_its_levels_have_names_of_their_own() -> None:
    names = [level.name for level in RUST_PAN.levels]
    assert len(set(names)) == len(names)
