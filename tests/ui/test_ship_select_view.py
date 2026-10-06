from dataclasses import replace

import pytest

from pewpy.game.player import SHIPS
from pewpy.ui.ship_select_view import characteristics, details

SHIP_LIST = list(SHIPS.values())


def test_each_ship_has_bars_for_the_same_characteristics_scaled_to_the_best() -> None:
    bars = characteristics(SHIP_LIST)
    assert len(bars) == len(SHIP_LIST)
    assert all([name for name, _ in ship] == ["Armor", "Speed", "Size", "Repair"] for ship in bars)
    for row in range(4):
        shares = [ship[row][1] for ship in bars]
        assert max(shares) == pytest.approx(1.0)
        assert all(0.0 <= share <= 1.0 for share in shares)


def test_the_bars_tell_the_ships_apart() -> None:
    bars = dict(zip(SHIPS, characteristics(SHIP_LIST), strict=True))
    assert bars["juggernaut"][0][1] == 1.0  # the most armor
    assert bars["phantom"][1][1] == 1.0  # the fastest
    assert bars["phantom"][3][1] == 1.0  # the best repairs
    assert 0.0 < bars["juggernaut"][3][1] < bars["vanguard"][3][1] < 1.0


def test_details_give_the_numbers_and_the_repair_only_when_there_is_one() -> None:
    assert "Health 8" in details(SHIPS["juggernaut"])
    assert "Repairs 0.5 health a second" in details(SHIPS["phantom"])
    assert "Repairs" not in details(replace(SHIPS["juggernaut"], regeneration=0.0))
