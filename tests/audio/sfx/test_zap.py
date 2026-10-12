from pewpy.audio.sfx.zap import zap
from tests.audio.sfx.audible import assert_audible


def test_the_zap_is_audible() -> None:
    assert_audible(zap(), 0.18)
