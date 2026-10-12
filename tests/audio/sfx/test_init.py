import numpy as np
import pytest

from pewpy.audio import sfx
from pewpy.audio.sfx import EFFECTS
from pewpy.audio.synth import RATE


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_every_effect_is_short_audible_and_in_range(name: str) -> None:
    sound = EFFECTS[name]()
    assert sound.ndim == 1
    assert 0.03 * RATE <= len(sound) <= 3 * RATE
    assert 0.01 < np.max(np.abs(sound)) <= 1.0


def test_every_effect_is_named_after_its_function() -> None:
    assert all(make is getattr(sfx, name) for name, make in EFFECTS.items())
