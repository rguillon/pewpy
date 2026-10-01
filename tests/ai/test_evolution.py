import numpy as np
import pytest

from pewpy.ai.evolution import Evolution, ranks


def test_ranks_keep_only_the_order():
    assert ranks(np.array([3.0, 100.0, -5.0])) == pytest.approx([0.0, 0.5, -0.5])


def test_evolution_climbs_towards_a_better_spot():
    target = np.array([1.0, -2.0, 0.5])
    evolution = Evolution(np.zeros(3), np.random.default_rng(0), population=20, noise=0.1, learning_rate=0.05)
    for _ in range(300):
        nudges, tries = evolution.ask()
        evolution.tell(nudges, np.array([-np.sum((w - target) ** 2) for w in tries]))
    assert np.linalg.norm(evolution.weights - target) < 0.3
    assert evolution.generation == 300


def test_tries_come_in_mirrored_pairs():
    evolution = Evolution(np.zeros(4), np.random.default_rng(1), population=6)
    nudges, tries = evolution.ask()
    assert len(nudges) == 3 and len(tries) == 6
    assert tries[0] == pytest.approx(-tries[1])


def test_an_odd_population_is_refused():
    with pytest.raises(ValueError, match="even"):
        Evolution(np.zeros(2), np.random.default_rng(0), population=5)
