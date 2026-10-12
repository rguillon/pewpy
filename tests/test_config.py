import json

import pytest

from pewpy import config
from pewpy.data import data_folder


def test_the_rules_are_read_from_the_data() -> None:
    rules = json.loads((data_folder() / "rules.json").read_text())
    assert rules["player"]["lives"] == config.PLAYER_LIVES
    assert rules["player"]["max_lives"] == config.MAX_LIVES
    assert rules["pickups"]["speed"] == config.PICKUP_SPEED
    assert rules["enemies"]["bullet_damage"] == config.ENEMY_BULLET_DAMAGE
    assert rules["bosses"]["beaten_time"] == config.BOSS_BEATEN_TIME


def test_the_play_area_has_the_windows_shape() -> None:
    assert pytest.approx(config.WINDOW_WIDTH / config.WINDOW_HEIGHT) == config.PLAY_WIDTH / config.PLAY_HEIGHT
    assert pytest.approx(config.PLAY_WIDTH) == config.WIDTH_SCALE * 1.5


def test_a_drop_is_an_upgrade_a_life_a_secondary_weapon_or_else_a_repair() -> None:
    shares = config.PICKUP_UPGRADE_SHARE + config.PICKUP_LIFE_SHARE + config.PICKUP_SECONDARY_SHARE
    assert 0 < shares < 1


def test_the_player_starts_in_the_bottom_half_with_lives_to_spare() -> None:
    assert -config.PLAY_HEIGHT / 2 < config.PLAYER_START_Y < 0
    assert 0 < config.PLAYER_LIVES <= config.MAX_LIVES


def test_every_model_is_made_of_the_swarmers_cubes() -> None:
    assert pytest.approx(0.06 / 9) == config.MODEL_VOXEL
