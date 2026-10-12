import pytest

from pewpy import config
from pewpy.game.weapons.guns.gun import MIDDLE, Gun, distance, parse_gun


def test_distances_can_be_shares_of_the_size_cubes_or_sums() -> None:
    assert distance(0.3, 0.2, 0.4) == 0.3
    assert distance("0.5w", 0.2, 0.4) == pytest.approx(0.1)
    assert distance("-0.5h", 0.2, 0.4) == pytest.approx(-0.2)
    assert distance("3v", 0.2, 0.4) == pytest.approx(3 * config.MODEL_VOXEL)
    assert distance("0.5w-0.05", 0.2, 0.4) == pytest.approx(0.05)
    assert distance("-0.5w+0.05", 0.2, 0.4) == pytest.approx(-0.05)
    with pytest.raises(ValueError, match="3x"):
        distance("3x", 0.2, 0.4)


def test_a_gun_fires_one_shot_straight_from_its_middle_unless_told() -> None:
    gun = Gun("fan", 1.0, 0.5)
    assert (gun.count, gun.volley, gun.origins, gun.reload, gun.off_screen) == (1, 1, MIDDLE, "reset", "hold")


def test_a_gun_is_read_with_lists_for_tuples_and_its_rate() -> None:
    gun = parse_gun({
        "from": "left arm",
        "pattern": "fan",
        "rate": 4,
        "speed": 0.5,
        "angles": [-10, 10],
        "origins": [["0.5w", 0], [-0.1, 0]],
        "velocities": [[0.1, -0.5]],
    })
    assert gun == Gun("fan", 0.25, 0.5, angles=(-10, 10), origins=(("0.5w", 0), (-0.1, 0)), velocities=((0.1, -0.5),))


def test_a_gun_can_fire_from_one_of_its_models_weapons() -> None:
    assert parse_gun({"pattern": "fan", "interval": 1, "speed": 0.5, "weapon": 2}).weapons == (2,)


def test_a_sequences_guns_need_no_interval_nor_speed() -> None:
    gun = parse_gun({"pattern": "fan", "interval": 1, "speed": 0.0, "sequence": [{"pattern": "ring", "count": 8}]})
    assert gun.sequence == (Gun("ring", 0.0, 0.0, count=8),)


def test_a_gun_fires_from_its_origins_or_its_weapons_not_both() -> None:
    with pytest.raises(ValueError, match="not both"):
        parse_gun({"pattern": "fan", "interval": 1, "speed": 0.5, "origins": [[0, 0]], "weapons": [1]})
