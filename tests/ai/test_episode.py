import numpy as np
import pytest

from pewpy.ai import episode
from pewpy.ai.brain import Brain, parameter_count
from pewpy.ai.episode import Outcome, boss_time, play
from pewpy.game.level import Level, Wave

EMPTY = Level(name="empty", scroll_speed=0.2, waves=())
DRONES = Level(name="drones", scroll_speed=0.2, waves=(Wave(time=1.0, enemy="drone", count=3),))


def idle() -> Brain:
    return Brain(np.zeros(parameter_count()))


def firing() -> Brain:
    """Stays put, the fire button held."""
    brain = Brain(np.zeros(parameter_count()))
    brain.layers[-2][-1, 2] = 1.0  # the output layer's bias for the fire button
    return brain


def test_an_empty_level_is_cleared_at_once():
    outcome = play(EMPTY, idle(), "vanguard", seed=0)
    assert outcome.cleared and outcome.progress == 2.0 and outcome.lives_lost == 0
    assert outcome.health_left == 1.0


def test_a_run_ends_when_the_level_is_over_and_its_fitness_counts_clearing_it():
    outcome = play(DRONES, firing(), "vanguard", seed=0)
    assert outcome.time < boss_time(DRONES) + episode.OVERTIME + 1
    lost = Outcome(cleared=False, time=outcome.time, progress=0.5, score=outcome.score, lives_lost=1, health_left=0.0)
    assert outcome.cleared
    assert outcome.fitness > lost.fitness + episode.CLEARED - 1


def test_fitness_grows_with_time_score_and_the_boss_damaged():
    base = Outcome(cleared=False, time=10.0, progress=0.5, score=0, lives_lost=1, health_left=0.0)
    assert Outcome(False, 20.0, 0.5, 0, 1, 0.0).fitness > base.fitness
    assert Outcome(False, 10.0, 0.5, 1000, 1, 0.0).fitness > base.fitness
    assert Outcome(False, 10.0, 1.5, 0, 1, 0.0).fitness == pytest.approx(base.fitness + episode.BOSS_DAMAGE / 2)
