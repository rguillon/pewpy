from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from pewpy.ai import files, rating
from pewpy.ai.brain import Brain, parameter_count
from pewpy.ai.episode import Outcome
from pewpy.ai.rating import rate, summarize
from pewpy.game.level import Level, Wave

LEVELS = (
    ("1-1", Level(name="Empty", scroll_speed=0.2, waves=())),
    ("1-2", Level(name="Drones", scroll_speed=0.2, waves=(Wave(time=0.5, enemy="drone", count=2),))),
)


@pytest.fixture(autouse=True)
def small_game(monkeypatch):
    monkeypatch.setattr(rating, "places", lambda: LEVELS)


def test_a_rating_is_the_share_of_runs_cleared():
    runs = [Outcome(True, 50, 2.0, 0, 0, 1.0), Outcome(False, 30, 0.5, 0, 5, 0.0), Outcome(True, 60, 2.0, 0, 2, 0.5)]
    summary = summarize("1-1", LEVELS[0][1], runs)
    assert summary.clear_rate == pytest.approx(66.7)
    assert summary.progress == pytest.approx(1.5)
    assert summary.lives_lost == pytest.approx(7 / 3, abs=0.01)


def test_every_level_is_rated_for_every_ship_with_a_brain_and_saved(tmp_path):
    files.save_training(tmp_path, "vanguard", files.Training(Brain(np.zeros(parameter_count())), 30))
    seen = []
    ratings = rate(
        ["vanguard", "juggernaut"], tmp_path, runs=2, executor=ThreadPoolExecutor(2), report=lambda s, r: seen.append(s)
    )
    assert list(ratings["ships"]) == ["vanguard"]  # the juggernaut has no brain yet
    levels = ratings["ships"]["vanguard"]["levels"]
    assert [level["place"] for level in levels] == ["1-1", "1-2"]
    assert levels[0]["clear_rate"] == 100.0  # an empty level
    assert ratings["ships"]["vanguard"]["generation"] == 30
    assert files.load_ratings(tmp_path) == ratings
    assert seen == ["vanguard", "vanguard"]


def test_a_stopped_rating_is_not_saved(tmp_path):
    files.save_training(tmp_path, "vanguard", files.Training(Brain(np.zeros(parameter_count()))))
    rate(["vanguard"], tmp_path, runs=1, executor=ThreadPoolExecutor(1), stop=lambda: True)
    assert files.load_ratings(tmp_path) is None
