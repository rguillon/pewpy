"""The pieces ships and bosses are made of, on their own."""

import random

import pytest

from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.bosses.details import trim
from pewpy.makers.bosses.weapons import core_guns
from pewpy.makers.components import COMPONENTS
from pewpy.makers.ships.kit import archetypes, extras, weapons
from pewpy.makers.ships.kit.hulls import HULLS, _along, hull
from pewpy.makers.ships.kit.ship import Ship
from pewpy.makers.ships.kit.wings import Wing


def test_an_empty_plan_is_not_trimmed() -> None:
    cv = Canvas(3, 2)
    trim(cv, symmetric=True)
    assert (cv.w, cv.h) == (3, 2)


def test_guns_crowd_together_when_they_dont_fit() -> None:
    cv = Canvas(5, 3)
    cv.rect(1, 3, 0, 2, "h")
    guns = core_guns(cv, 9, symmetric=True)
    assert 0 < len(guns) < 9
    assert all(cv.get(round(x), round(y)) == "r" for _, x, y in guns)


def test_a_ship_without_weapons_gets_guns_in_its_nose(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(archetypes, "_player_weapons", lambda *_: None)
    monkeypatch.setattr(archetypes, "_sometimes", lambda *_: None)  # no equipment: its missile racks are armed
    assert archetypes.player_ship(random.Random(1), "vanguard").weapons
    ship = Ship()
    body = hull(random.Random(1), ship, "dart", 12, 2.0, 2.0)
    archetypes._finish(random.Random(1), ship, body)
    assert ship.weapons


def test_a_heavy_without_wing_tips_has_no_tip_nacelles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(archetypes, "_wings", lambda *_, **__: Wing([], 0, {}))
    ship = archetypes.heavy(random.Random(2))
    assert not ship.nozzles or all(nozzle.x == 0 or abs(nozzle.x) < 6 for nozzle in ship.nozzles)


def test_wingless_ships_get_no_wing_weapons_nor_stripes() -> None:
    ship = Ship()
    no_wing = Wing([], 0, {})
    weapons.wing_guns(random.Random(1), ship, no_wing, 0.5)
    weapons.tip_weapons(random.Random(1), ship, no_wing)
    extras.wing_stripes(random.Random(1), ship)
    assert not ship.cells
    assert not ship.weapons


def test_past_its_nose_a_hull_keeps_its_last_profile() -> None:
    profile = HULLS["dart"][0]
    assert _along(profile, 1.5) == profile[-1]


def test_a_ship_tells_its_cubes_and_lopsided_engines() -> None:
    ship = Ship()
    ship.put(0, 0, 0, "h")
    assert ship.get(0, 0, 0) == "h"
    assert ship.get(1, 0, 0) is None
    ship.nozzle(2, 0, 0, 1.0, mirror=False)
    assert not ship.symmetric
    assert len(ship.nozzles) == 1


def test_a_plan_ignores_cells_outside_it() -> None:
    cv = Canvas(2, 2)
    cv.set(5, 0, "h")
    assert cv.rows_chars() == ""


def test_a_built_in_part_off_the_axis_is_a_pair_with_its_engines() -> None:
    ship = Ship()
    ship.stamp(COMPONENTS["engine"](random.Random(1), 1), -4, 0, 0)
    assert len(ship.nozzles) == 2  # mirrored
    assert ship.symmetric
    on_axis = Ship()
    on_axis.stamp(COMPONENTS["turret"](random.Random(3), 1), 0, 0, 0)
    assert len({(x, y) for _, x, y, _ in [(w.kind, w.x, w.y, w.z) for w in on_axis.weapons]}) == len(on_axis.weapons)
