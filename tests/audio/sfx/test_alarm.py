import numpy as np

from pewpy.audio.sfx.alarm import alarm
from pewpy.audio.synth import RATE
from tests.audio.sfx.audible import assert_audible


def test_the_alarm_is_audible() -> None:
    assert_audible(alarm(), 1.5)


def test_the_alarm_wails_three_times() -> None:
    sound = alarm()
    quarters = np.array_split(np.abs(sound[: RATE * 3 // 2]), 6)  # its two tones change every quarter second
    assert all(np.max(each) > 0.01 for each in quarters)
