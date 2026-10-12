from pewpy.audio.sfx.pickup import pickup
from tests.audio.sfx.audible import assert_audible


def test_the_pickup_arpeggio_is_audible() -> None:
    assert_audible(pickup(), 4 * 0.06)
