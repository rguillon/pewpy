from pewpy.audio.sfx.disarmed import disarmed
from tests.audio.sfx.audible import assert_audible


def test_the_disarmed_crunch_is_audible() -> None:
    assert_audible(disarmed(), 0.3)
