from pewpy.audio.sfx.extra_life import extra_life
from tests.audio.sfx.audible import assert_audible


def test_the_extra_life_fanfare_is_audible() -> None:
    assert_audible(extra_life(), 6 * 0.07 + 0.35)
