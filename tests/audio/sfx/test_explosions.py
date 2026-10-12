from collections.abc import Callable

import numpy as np
import pytest

from pewpy.audio.sfx.explosions import blast, explosion, explosion_big, explosion_small, player_explosion
from pewpy.audio.synth import FloatArray
from tests.audio.sfx.audible import assert_audible


@pytest.mark.parametrize(
    ("make", "seconds"),
    [(explosion_small, 0.45), (explosion, 0.9), (explosion_big, 2.4), (player_explosion, 1.6), (blast, 0.5)],
)
def test_every_explosion_is_audible(make: Callable[[], FloatArray], seconds: float) -> None:
    assert_audible(make(), seconds)


def test_bigger_explosions_are_louder() -> None:
    assert np.max(np.abs(explosion_small())) < np.max(np.abs(explosion())) < np.max(np.abs(explosion_big()))
