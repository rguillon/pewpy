from pewpy.audio.sfx.switch import switch
from tests.audio.sfx.audible import assert_audible


def test_the_switch_blips_are_audible() -> None:
    assert_audible(switch(), 0.04 + 0.015 + 0.05)
