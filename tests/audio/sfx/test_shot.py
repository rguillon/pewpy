from pewpy.audio.sfx.shot import shot
from tests.audio.sfx.audible import assert_audible


def test_the_shot_is_audible() -> None:
    assert_audible(shot(), 0.09)
