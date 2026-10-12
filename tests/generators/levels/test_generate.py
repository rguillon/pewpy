"""Making every level of every world."""

import pytest

from pewpy.game.enemies.kinds import FINAL_BOSSES, MINI_BOSSES
from pewpy.game.level import parse_level
from pewpy.generators.levels.__main__ import DEFAULT_SEED
from pewpy.generators.levels.difficulty import SCROLL_SPEED, between, difficulty
from pewpy.generators.levels.enemies import GROUND
from pewpy.generators.levels.generate import generate
from pewpy.generators.levels.waves import AFTER_MINI_BOSS, BOSS_DELAY, FIRST_WAVE
from pewpy.generators.levels.worlds import WORLDS

LEVELS_MADE = generate(DEFAULT_SEED)


def test_the_same_seed_makes_the_same_levels_and_another_one_other_waves() -> None:
    assert generate(DEFAULT_SEED) == LEVELS_MADE
    other = generate(DEFAULT_SEED + 1)
    assert other.keys() == LEVELS_MADE.keys()
    assert other[1, 1]["waves"] != LEVELS_MADE[1, 1]["waves"]
    assert other[1, 1]["name"] == LEVELS_MADE[1, 1]["name"]


def test_every_level_is_read_by_the_game() -> None:
    for (w, n), level in LEVELS_MADE.items():
        assert parse_level(level, f"{w}-{n}").scroll_speed == round(between(SCROLL_SPEED, difficulty(w, n)), 3)


def test_each_level_has_its_mini_boss_halfway_and_its_final_boss_last() -> None:
    for (w, n), level in LEVELS_MADE.items():
        plan = WORLDS[w - 1].levels[n - 1]
        enemies = [wave["enemy"] for wave in level["waves"]]
        assert enemies.count(plan.mini_boss) == 1
        assert plan.mini_boss in MINI_BOSSES
        assert plan.final_boss in FINAL_BOSSES
        assert enemies[-1] == plan.final_boss
        waves = level["waves"]
        mini = enemies.index(plan.mini_boss)
        assert waves[0]["time"] == FIRST_WAVE
        assert waves[mini]["time"] == pytest.approx(waves[mini - 1]["time"] + BOSS_DELAY, abs=0.11)
        assert waves[mini + 1]["time"] == pytest.approx(waves[mini]["time"] + AFTER_MINI_BOSS, abs=0.11)
        assert waves[-1]["time"] == pytest.approx(waves[-2]["time"] + BOSS_DELAY, abs=0.11)


def test_worlds_without_ground_units_send_no_ground_enemies() -> None:
    for (w, _), level in LEVELS_MADE.items():
        if not WORLDS[w - 1].ground_units:
            assert not {wave["enemy"] for wave in level["waves"]} & GROUND
