"""Evolution strategies on a flat vector of weights."""

import numpy as np
import pytest

from pewpy.generators.ai_training.evolution import Evolution, ranks


def test_ranks_keep_only_the_order() -> None:
    assert list(ranks(np.array([10.0, -3.0, 500.0]))) == [0.0, -0.5, 0.5]
    assert list(ranks(np.array([7.0]))) == [-0.5]


@pytest.mark.parametrize("population", [0, 3])
def test_the_population_is_even(population: int) -> None:
    with pytest.raises(ValueError, match="even"):
        Evolution(np.zeros(2), np.random.default_rng(0), population=population)


def test_the_tries_are_mirrored_nudges() -> None:
    evolution = Evolution(np.ones(3), np.random.default_rng(1), population=4, noise=0.1)
    nudges, tries = evolution.ask()
    assert nudges.shape == (2, 3)
    assert len(tries) == 4
    assert np.allclose(tries[0] - 1, -(tries[1] - 1))  # a nudge and its opposite


def test_the_weights_move_towards_the_better_tries() -> None:
    target = np.array([0.5, -0.3, 0.2])
    evolution = Evolution(np.zeros(3), np.random.default_rng(2), population=16, learning_rate=0.02)
    start = np.linalg.norm(evolution.weights - target)
    for _ in range(150):
        nudges, tries = evolution.ask()
        evolution.tell(nudges, np.array([-np.linalg.norm(weights - target) for weights in tries]))
    assert evolution.generation == 150
    assert np.linalg.norm(evolution.weights - target) < start / 3
