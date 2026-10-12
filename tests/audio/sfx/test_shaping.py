import numpy as np
import pytest

from pewpy.audio.sfx.shaping import boom, fade, glide, span
from pewpy.audio.synth import RATE


def test_a_span_is_the_times_of_its_samples() -> None:
    times = span(0.5)
    assert len(times) == RATE // 2
    assert times[0] == 0.0
    assert times[1] == pytest.approx(1 / RATE)


def test_a_glide_goes_from_its_start_to_its_end() -> None:
    hertz = glide(0.1, 1000, 250)
    assert hertz[0] == pytest.approx(1000)
    assert hertz[-1] == pytest.approx(250, rel=0.01)
    assert np.all(np.diff(hertz) < 0)


def test_a_curved_glide_moves_faster_at_first() -> None:
    straight, curved = glide(0.1, 1000, 250), glide(0.1, 1000, 250, curve=3.0)
    middle = len(straight) // 2
    assert curved[middle] < straight[middle]


def test_a_fade_rises_quickly_then_decays() -> None:
    shaped = fade(np.ones(RATE // 2), decay=0.05, attack=0.01)
    assert shaped[0] == 0.0
    assert shaped[int(0.01 * RATE)] == pytest.approx(np.exp(-0.01 / 0.05), rel=0.01)
    assert shaped[-1] < 0.001


def test_a_boom_is_loud_then_fades_and_stays_in_range() -> None:
    sound = boom(0.5, 3000, 120, 1)
    assert len(sound) == RATE // 2
    assert np.max(np.abs(sound)) <= 0.8
    assert np.std(sound[: RATE // 10]) > 10 * np.std(sound[-RATE // 10 :])
