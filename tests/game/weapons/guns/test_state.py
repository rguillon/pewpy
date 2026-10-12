from typing import Any

import pytest

from pewpy.game.weapons.guns.state import GunState


def test_a_gun_starts_with_nothing_under_way() -> None:
    state = GunState(cooldown=0.5)
    assert not state.busy
    assert (state.shots, state.volleys, state.item) == (0, 0, None)


@pytest.mark.parametrize("busy", [{"volley_left": 1}, {"charging": 0.1}, {"beaming": 0.1}])
def test_a_gun_is_busy_mid_volley_charging_or_beaming(busy: dict[str, Any]) -> None:
    assert GunState(cooldown=0.0, **busy).busy


def test_a_laser_charging_its_beams_is_not_busy() -> None:
    assert not GunState(cooldown=0.0, charge=0.5).busy
