import pytest

from pewpy.audio.synth.signal import frequency


@pytest.mark.parametrize(("pitch", "hertz"), [(69, 440.0), (81, 880.0), (57, 220.0), (60, 261.63)])
def test_a_midi_pitch_has_its_frequency(pitch: int, hertz: float) -> None:
    assert frequency(pitch) == pytest.approx(hertz, abs=0.01)
