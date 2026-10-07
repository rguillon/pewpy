"""Playing a level with a brain, headless."""

import numpy as np
import pytest

from pewpy.ai.brain import Brain
from pewpy.ai.training import episode
from pewpy.ai.training.episode import Outcome, boss_time, play
from pewpy.game.entities import Pickup
from pewpy.game.level import Level, Wave
from pewpy.game.world import World

from .conftest import DRONES, EMPTY

BRAIN = Brain.random(np.random.default_rng(0))


def test_a_runs_fitness_counts_how_far_it_got_and_more_when_it_cleared_the_level() -> None:
    lost = Outcome(cleared=False, time=10, progress=0.5, score=500, lives_lost=1, health_left=0.0, advanced=10.0)
    assert lost.fitness == pytest.approx(10.0 + 500 * episode.PER_POINT)
    won = Outcome(cleared=True, time=10, progress=2.0, score=0, lives_lost=0, health_left=1.0, bosses=1.0, pickups=2)
    expected = episode.CLEARED + episode.HEALTH_LEFT + episode.BOSS_DAMAGE + 2 * episode.PER_PICKUP
    assert won.fitness == pytest.approx(expected)


def test_the_final_boss_comes_with_the_last_wave() -> None:
    assert boss_time(DRONES) == pytest.approx(0.1)
    assert boss_time(EMPTY) == 0.0


def test_a_level_cleared_is_all_the_way() -> None:
    outcome = play(EMPTY, BRAIN, "vanguard", seed=1)
    assert outcome.cleared
    assert outcome.progress == 2.0
    assert outcome.health_left == pytest.approx(1.0)


def test_a_run_gives_up_on_a_boss_it_can_not_beat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(episode, "OVERTIME", 1.0)
    boss = Level(name="boss", scroll_speed=0.2, waves=(Wave(time=0.0, enemy="harvester"),))
    outcome = play(boss, BRAIN, "juggernaut", seed=2)
    assert not outcome.cleared
    assert outcome.time == pytest.approx(1.0, abs=0.05)
    assert 1.0 <= outcome.progress < 2.0  # at the final boss, some of it destroyed maybe


def test_a_mini_boss_is_not_the_final_one(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(episode, "OVERTIME", 0.3)
    level = Level(
        name="two bosses", scroll_speed=0.2, waves=(Wave(time=0.0, enemy="harvester"), Wave(time=0.5, enemy="warden"))
    )
    outcome = play(level, BRAIN, "vanguard", seed=3)
    assert not outcome.cleared
    assert outcome.progress <= 1.0  # the final boss never came: not past half way


def test_a_run_stopped_early_got_part_of_the_way(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(episode, "OVERTIME", -0.5)  # it gives up before the boss is due
    level = Level(name="long", scroll_speed=0.2, waves=(Wave(time=1.0, enemy="harvester"),))
    outcome = play(level, BRAIN, "vanguard", seed=4)
    assert 0.0 < outcome.progress < 1.0


def test_a_life_lost_starts_the_level_again_and_pickups_are_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    class Unlucky(World):
        """The first update takes a life; then a pickup comes right onto the ship."""

        updates = 0

        def update(self, dt: float, controls: object) -> None:
            self.updates += 1
            if self.updates == 1:
                self.player.health = 0.0
            elif self.updates == 2:
                self.pickups.append(Pickup(x=self.player.x, y=self.player.y, kind="repair"))
            super().update(dt, controls)  # ty: ignore[invalid-argument-type]

    monkeypatch.setattr(episode, "World", Unlucky)
    short = Level(name="short", scroll_speed=0.2, waves=(Wave(time=0.2),))  # nothing comes: cleared at 0.2 s
    outcome = play(short, BRAIN, "vanguard", seed=5, lives=3)
    assert outcome.lives_lost == 1
    assert outcome.cleared
