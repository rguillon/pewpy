from pewpy.audio.sfx.hurt import hurt
from tests.audio.sfx.audible import assert_audible


def test_the_hurt_buzz_is_audible() -> None:
    assert_audible(hurt(), 0.22)
