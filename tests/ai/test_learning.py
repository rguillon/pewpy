from concurrent.futures import ThreadPoolExecutor

import pytest

from pewpy.ai import files, learning
from pewpy.ai.learning import Learner, learn
from pewpy.game.level import Level, Wave

LEVELS = (
    Level(name="empty", scroll_speed=0.2, waves=()),
    Level(name="drones", scroll_speed=0.2, waves=(Wave(time=0.5, enemy="drone", count=2),)),
)


@pytest.fixture(autouse=True)
def small_game(monkeypatch):
    monkeypatch.setattr(learning, "_levels", lambda: LEVELS)
    monkeypatch.setattr(learning, "CHECK_EVERY", 2)
    monkeypatch.setattr("pewpy.ai.evolution.POPULATION", 4)


def test_a_learner_steps_checks_and_saves_its_brain(tmp_path):
    with ThreadPoolExecutor(2) as executor:
        learner = Learner("vanguard", tmp_path, executor)
        learner.evolution.population = 4
        first = learner.step()
        second = learner.step()
    assert (first.generation, first.cleared) == (1, None)
    assert second.generation == 2 and second.cleared is not None and 0.0 <= second.cleared <= 1.0
    assert second.progress is not None and second.cleared <= second.progress <= 1.0
    saved = files.load_training(tmp_path, "vanguard")
    assert saved is not None and saved.generation == 2 and saved.history[-1]["cleared"] == second.cleared


def test_learning_goes_on_from_the_saved_brain(tmp_path):
    with ThreadPoolExecutor(2) as executor:
        learner = Learner("vanguard", tmp_path, executor)
        learner.evolution.population = 4
        learner.step()
        learner.save()
        again = Learner("vanguard", tmp_path, executor)
    assert again.training.generation == 1
    assert (again.brain.weights == learner.brain.weights).all()


def test_learn_trains_every_ship_in_turns_until_told_to_stop(tmp_path, monkeypatch):
    monkeypatch.setattr(learning, "Evolution", _small_evolution)
    reports, brains = [], []
    learn(
        ["vanguard", "juggernaut"],
        2,
        tmp_path,
        report=reports.append,
        executor=ThreadPoolExecutor(2),
        on_brain=lambda ship, brain: brains.append(ship),
    )
    assert [(report.ship, report.generation) for report in reports] == [
        ("vanguard", 1),
        ("vanguard", 2),
        ("juggernaut", 1),
        ("juggernaut", 2),
    ]
    assert brains == ["vanguard", "vanguard", "juggernaut", "juggernaut"]


def test_learning_stops_when_told_and_saves_only_the_ships_that_learned(tmp_path, monkeypatch):
    monkeypatch.setattr(learning, "Evolution", _small_evolution)
    stopped: list = []
    learn(
        ["vanguard", "juggernaut"],
        0,
        tmp_path,
        report=stopped.append,
        executor=ThreadPoolExecutor(1),
        stop=lambda: len(stopped) >= 1,
    )
    assert len(stopped) == 1
    assert files.load_training(tmp_path, "vanguard") is not None
    assert files.load_training(tmp_path, "juggernaut") is None


def _small_evolution(weights, rng, **kwargs):
    from pewpy.ai.evolution import Evolution

    return Evolution(weights, rng, population=4)
