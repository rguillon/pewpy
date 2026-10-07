"""The win rates, on tiny levels, in this process."""

import numpy as np
import pytest

from pewpy.ai.brain import Brain
from pewpy.generators.ai_training.winrate import win_rates, win_run

BRAIN = Brain.random(np.random.default_rng(0))


@pytest.mark.usefixtures("tiny_levels")
def test_every_level_is_played_with_every_ship() -> None:
    shown: list[tuple[str, str]] = []
    rates = win_rates(BRAIN, ["vanguard", "phantom"], runs=2, report=lambda place, name, _: shown.append((place, name)))
    assert list(rates) == ["1-1", "1-2", "2-1", "2-2"]
    assert rates["1-1"] == {"vanguard": 1.0, "phantom": 1.0}  # cleared at once
    assert shown[0] == ("1-1", "empty")
    assert win_run((BRAIN.weights, BRAIN.hidden, "vanguard", 0, 1, 1))
