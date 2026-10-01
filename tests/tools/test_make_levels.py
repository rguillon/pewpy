import json

import pytest

from pewpy.game.boss_catalog import BOSSES
from pewpy.game.level import load_levels, parse_level
from pewpy.game.roster import ENEMY_TYPES
from tools import make_levels
from tools.make_levels import DEFAULT_SEED, SHAPES, UNLOCK, WORLDS, difficulty, generate, threat

LEVELS = generate(DEFAULT_SEED)


def test_the_games_levels_are_the_ones_the_tool_makes():
    assert [parse_level(level) for level in LEVELS.values()] == load_levels()


def test_a_worlds_first_level_is_as_hard_as_the_third_of_the_world_before():
    assert [difficulty(1, n) for n in range(1, 7)] == [1, 2, 3, 4, 5, 6]
    assert all(difficulty(w, 1) == difficulty(w - 1, 3) for w in range(2, len(WORLDS) + 1))
    assert difficulty(len(WORLDS), 6) == make_levels.MAX_DIFFICULTY


def test_harder_levels_send_more_and_scroll_faster():
    for (w, n), level in LEVELS.items():
        d = difficulty(w, n)
        budget = (
            make_levels.THREAT[0]
            + (make_levels.THREAT[1] - make_levels.THREAT[0])
            * ((d - 1) / (make_levels.MAX_DIFFICULTY - 1)) ** make_levels.THREAT_CURVE
        )
        biggest = max(threat(wave) for wave in level["waves"][:-1])
        assert budget <= sum(threat(wave) for wave in level["waves"][:-1]) <= budget + biggest
    speeds = [LEVELS[1, n]["scroll_speed"] for n in range(1, 7)]
    assert speeds == sorted(speeds) and len(set(speeds)) == 6


def test_enemies_come_once_unlocked_and_never_on_the_ground_over_water():
    for (w, n), level in LEVELS.items():
        enemies = {wave["enemy"] for wave in level["waves"][:-1]}
        assert all(UNLOCK[enemy] <= difficulty(w, n) for enemy in enemies)
        if not WORLDS[w - 1].ground_units:
            assert not any(ENEMY_TYPES[enemy].ground for enemy in enemies)


def test_every_enemy_can_come_and_comes_somewhere():
    assert set(UNLOCK) == set(SHAPES) == set(ENEMY_TYPES)
    sent = {wave["enemy"] for level in LEVELS.values() for wave in level["waves"][:-1]}
    assert sent == set(ENEMY_TYPES)


def test_each_level_ends_with_its_boss_and_each_world_keeps_its_ground():
    assert sorted(plan.boss for world in WORLDS for plan in world.levels) == sorted(BOSSES)
    for (w, n), level in LEVELS.items():
        assert level["waves"][-1]["enemy"] == WORLDS[w - 1].levels[n - 1].boss
        assert level["background"] == WORLDS[w - 1].background


def test_the_same_seed_makes_the_same_levels_and_another_new_waves():
    assert generate(DEFAULT_SEED) == LEVELS
    other = generate(DEFAULT_SEED + 1)
    assert other[1, 1]["waves"] != LEVELS[1, 1]["waves"]
    assert other[1, 1]["name"] == LEVELS[1, 1]["name"]  # the plan stays


def test_the_tool_writes_the_worlds(tmp_path, monkeypatch):
    (tmp_path / "world_9").mkdir()
    (tmp_path / "world_9" / "level_1.json").write_text("{}")
    (tmp_path / "sceneries.json").write_text("{}")
    monkeypatch.setattr("sys.argv", ["make_levels", "--out", str(tmp_path)])
    make_levels.main()
    assert not (tmp_path / "world_9").exists()
    assert (tmp_path / "sceneries.json").exists()
    assert json.loads((tmp_path / "world_1" / "world.json").read_text()) == {"name": WORLDS[0].name}
    assert len(list(tmp_path.glob("world_*/level_*.json"))) == sum(len(world.levels) for world in WORLDS)


@pytest.mark.parametrize("enemy", sorted(SHAPES))
def test_every_shape_makes_a_wave_the_game_reads(enemy):
    rng = make_levels.random.Random(0)
    for _ in range(10):
        wave = make_levels.make_wave(rng, enemy, make_levels.MAX_DIFFICULTY)
        parse_level({"waves": [{"time": 1.0, **wave}]})
