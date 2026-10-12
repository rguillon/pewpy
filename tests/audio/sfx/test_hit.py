from pewpy.audio.sfx.hit import hit
from tests.audio.sfx.audible import assert_audible


def test_the_hit_tick_is_audible() -> None:
    assert_audible(hit(), 0.07)
