from dataclasses import replace

import pytest

from pewpy.game.player import SHIPS
from pewpy.ui.ship_select_view import BAR_WIDTH, COLUMN_SPACING, LABEL_WIDTH, characteristics, column_spacing, details

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


def test_a_test_ship_is_not_compared_with_the_others() -> None:
    regular = [replace(SHIP_LIST[0], health=4.0, test=False), replace(SHIP_LIST[0], health=8.0, test=False)]
    tester = replace(SHIP_LIST[0], health=99999.0, test=True)
    bars = characteristics([*regular, tester])
    assert [ship[0][1] for ship in bars] == [0.5, 1.0, 1.0]  # the regular ships' armor as without it; its own, full


def test_the_columns_fit_the_screen() -> None:
    assert column_spacing(3, 2.0) == COLUMN_SPACING  # a wide screen: the usual room
    assert column_spacing(4, 1.25) < COLUMN_SPACING
    assert 1.5 * column_spacing(4, 1.25) + (LABEL_WIDTH + BAR_WIDTH) / 2 < 1.25  # the outer columns stay on screen
