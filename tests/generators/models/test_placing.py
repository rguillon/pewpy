"""The ship maker when things don't go its way: no room for a part, nothing to stand on, hulls already touching."""

import random

import pytest

from pewpy.generators.models.parts import KINDS, of_kind
from pewpy.generators.models.parts.part import Sketch
from pewpy.generators.models.parts_browser import PartBrowser
from pewpy.generators.models.ships import modules
from pewpy.generators.models.ships.modules import _flat, _nose_guns
from pewpy.generators.models.ships.placing import Hull, Maker
from pewpy.generators.models.ships.ship import Ship, Spot


def maker(layout: str, seed: int = 1, wanted: tuple[float, float] = (60, 45)) -> Maker:
    made = Maker(random.Random(seed), wanted, forced=True)
    made.layout = layout
    return made


def nowhere(*_args: object, **_kwargs: object) -> None:
    return None


def never(*_args: object, **_kwargs: object) -> bool:
    return False


def test_a_lopsided_part_reaching_across_the_axis_goes_nowhere() -> None:
    made = maker("classic")
    made.frame()
    wing = of_kind("wing")[-1]  # a long one: from x = 2 it reaches well past the axis
    assert not wing.symmetric
    assert made._pair(Spot(2, 0, 0), wing) == []


def test_nothing_hangs_under_where_nothing_is() -> None:
    made = maker("classic")
    made.frame()
    assert made._under(of_kind("tank", "under")[0], 10_000, 0) is None


def test_wings_that_fit_nowhere_are_left_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Ship, "fits", never)
    made = maker("classic")
    made.frame()
    assert made.wings == []
    assert made.ship.nozzles  # the smallest nozzle all the same


def test_a_boom_with_nothing_on_its_tail_to_stand_on_gets_no_fin(monkeypatch: pytest.MonkeyPatch) -> None:
    made = maker("booms")
    monkeypatch.setattr(made, "_on_top", nowhere)
    made.frame()
    assert made.booms
    assert not any(placed.part.kind == "fin" for placed in made.ship.placed)


def test_hulls_already_touching_need_no_beam() -> None:
    made = maker("multihull")
    made.frame()
    before = len(made.ship.placed)
    main = made.hulls[0]
    made._connect(main, main, [-1, 1])  # the same hull: touching all along
    assert len(made.ship.placed) == before


def test_a_side_hull_that_doesnt_fit_ends_the_row(monkeypatch: pytest.MonkeyPatch) -> None:
    made = maker("multihull", wanted=(120, 90))
    monkeypatch.setattr(made, "_another_hull", never)
    made.frame()
    assert len(made.hulls) == 1


def test_a_city_with_no_room_on_its_deck_has_no_buildings(monkeypatch: pytest.MonkeyPatch) -> None:
    made = maker("city")
    made.frame()
    monkeypatch.setattr(made, "_on_top", nowhere)
    made._buildings()
    assert len(made.hulls) == 1


def test_wings_with_no_pod_thin_enough_get_no_engines_under_them(monkeypatch: pytest.MonkeyPatch) -> None:
    made = maker("classic")
    made.frame()
    nozzles = len(made.ship.nozzles)
    monkeypatch.setattr(made, "_thin", lambda _parts: [])
    made._wing_engines(tip=False)
    assert len(made.ship.nozzles) == nozzles


def test_a_cockpit_with_nowhere_to_go_is_left_off(monkeypatch: pytest.MonkeyPatch) -> None:
    made = maker("classic")
    made.frame()
    made.lopsided = {"tower"}
    monkeypatch.setattr(made, "_on_top", nowhere)
    monkeypatch.setattr(made, "_put", never)
    before = len(made.ship.placed)
    made._cockpit()
    assert len(made.ship.placed) == before


def test_a_module_whose_front_guns_fit_nowhere_goes_without(monkeypatch: pytest.MonkeyPatch) -> None:
    ship = Ship()
    platform = _flat(of_kind("hull")[20])
    ship.place(platform, [Spot(0, 0, 0)])
    monkeypatch.setattr(modules, "_put", never)
    _nose_guns(random.Random(1), ship, platform)
    assert len(ship.placed) == 1


def test_a_housing_one_cube_wide_has_no_inner_plate() -> None:
    sketch = Sketch()
    sketch.housing(0, 0, 4, 0, 1)
    assert set(sketch.cells.values()) <= {"N", "H", "k", "p"}
    assert "h" not in sketch.cells.values()


def test_the_parts_browser_counts_a_parts_weapons() -> None:
    browser = PartBrowser(list(KINDS).index("gun"))
    browser.index = next(index for index, part in enumerate(browser.parts) if len(part.weapons) > 1)
    assert f"{len(browser.part.weapons)} weapons" in browser.info()
    browser.index = next(index for index, part in enumerate(browser.parts) if len(part.weapons) == 1)
    assert browser.info().endswith("1 weapon")


def test_a_hull_view_knows_how_wide_it_gets() -> None:
    hull = Hull(of_kind("hull")[10])
    assert hull.broadest == max(half for half, _, _ in hull.part.rows.values())
