from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from pewpy.ai import files, learning, rating
from pewpy.ai.brain import Brain, parameter_count
from pewpy.ai.sessions import LearningSession, RatingSession
from pewpy.game.level import Level, Wave

EMPTY = Level(name="Empty", scroll_speed=0.2, waves=())
DRONES = Level(name="Drones", scroll_speed=0.2, waves=(Wave(time=0.5, enemy="drone"),))


@pytest.fixture(autouse=True)
def small_game(monkeypatch):
    monkeypatch.setattr(learning, "_levels", lambda: (EMPTY, DRONES))
    monkeypatch.setattr(learning, "CHECK_EVERY", 1)
    monkeypatch.setattr(rating, "places", lambda: (("1-1", EMPTY), ("1-2", DRONES)))


def test_learning_runs_in_the_background_until_stopped(tmp_path, monkeypatch):
    from pewpy.ai.evolution import Evolution

    monkeypatch.setattr(learning, "Evolution", lambda weights, rng: Evolution(weights, rng, population=2))
    session = LearningSession(["vanguard"], tmp_path, executor=ThreadPoolExecutor(1))
    assert session.brain("vanguard") is None  # nothing learned yet
    session.start()
    session.thread.join(timeout=0.01)
    while "vanguard" not in session.reports and not session.done:
        session.thread.join(timeout=0.05)
    session.stop(wait=30)
    assert session.done and session.error is None
    assert session.brain("vanguard") is not None
    assert "vanguard" in session.checks
    assert files.load_training(tmp_path, "vanguard") is not None


def test_a_session_shows_its_error_instead_of_crashing(tmp_path, monkeypatch):
    def broken(*args, **kwargs):
        msg = "no levels"
        raise RuntimeError(msg)

    monkeypatch.setattr("pewpy.ai.sessions.learn", broken)
    session = LearningSession(["vanguard"], tmp_path, executor=ThreadPoolExecutor(1))
    session.start()
    session.thread.join(timeout=10)
    assert session.done and session.error == "RuntimeError: no levels"


def test_rating_fills_its_table_and_saves_it(tmp_path):
    files.save_training(tmp_path, "vanguard", files.Training(Brain(np.zeros(parameter_count()))))
    session = RatingSession(["vanguard", "juggernaut"], tmp_path, runs=1, executor=ThreadPoolExecutor(1))
    assert session.ships == ["vanguard"]  # only the ships that learned
    session.start()
    session.thread.join(timeout=60)
    assert session.done and session.saved
    assert [rating.place for rating in session.table()["vanguard"]] == ["1-1", "1-2"]
    assert files.load_ratings(tmp_path) is not None
