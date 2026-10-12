from pewpy.audio.sfx.repair import repair
from tests.audio.sfx.audible import assert_audible


def test_the_repair_glide_is_audible() -> None:
    assert_audible(repair(), 0.4)
