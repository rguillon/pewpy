import pytest

from pewpy.audio.synth.instruments import BASS, BRASS, KEYS, LEAD, PAD, PLUCK, Instrument, instrument


@pytest.mark.parametrize(
    ("program", "expected"),
    [(38, BASS), (89, PAD), (50, PAD), (80, PLUCK), (98, PLUCK), (81, LEAD), (61, BRASS), (0, KEYS), (120, KEYS)],
)
def test_each_general_midi_family_has_an_instrument(program: int, expected: Instrument) -> None:
    assert instrument(program) is expected


def test_the_bass_and_pads_duck_under_the_kick_and_the_rest_do_not() -> None:
    assert BASS.ducks
    assert PAD.ducks
    assert not any(each.ducks for each in (LEAD, PLUCK, KEYS, BRASS))
