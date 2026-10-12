from pewpy.audio.sfx.missile import missile
from tests.audio.sfx.audible import assert_audible


def test_the_missile_whoosh_is_audible() -> None:
    assert_audible(missile(), 0.35)
