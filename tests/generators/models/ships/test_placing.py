"""Placing parts on a ship: its layout, its size, its symmetry; a boss's destroyable parts; when nothing fits."""

import random
from collections import Counter

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.geometry import miss
from pewpy.generators.models.common.palette import GREYS, pick_colors
from pewpy.generators.models.common.palette import palette as make_palette
from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.ships.placing import (
    CITY_LAYOUTS,
    COCKPIT_TALL,
    LAYOUTS,
    LOPSIDED,
    PLAYER_LAYOUTS,
    TALL,
    THICKER,
    Hull,
    Maker,
    make_ship,
    nose_room,
)
from pewpy.generators.models.ships.selection import FLAMES, finish
from pewpy.generators.models.ships.ship import Ship, Spot
from pewpy.graphics import models

COLORS = make_palette(GREYS, pick_colors(random.Random(0)))


def boss(seed: int, parts: int, *, symmetric: bool = True, wanted: tuple[float, float] = (50, 38)) -> dict:
    ship = make_ship(random.Random(seed), wanted, parts=parts, symmetric=symmetric, least_armed=5)
    return ship.drawing(COLORS, FLAMES[0])


def test_a_boss_is_drawn_apart_from_its_parts_all_readable_and_armed() -> None:
    for seed in range(8):
        drawings = boss(seed, 4, symmetric=seed % 3 != 0)
        for drawing in [drawings["core"], *(drawing for drawing, _, _ in drawings["parts"])]:
            assert len(pieces(models.parse_voxels(drawing).cells)) == 1  # every cube touching the others
        weapons = len(drawings["core"]["weapons"]) + sum(len(d.get("weapons", [])) for d, _, _ in drawings["parts"])
        assert weapons >= 5
        assert 1 <= len(drawings["groups"]) == len(drawings["parts"]) == len(drawings["kinds"]) <= 4


@pytest.mark.parametrize(("symmetric", "parts"), [(True, 4), (True, 5), (False, 3), (True, 12)])
def test_a_boss_gets_the_parts_asked_that_fit_a_group_sharing_its_drawing_and_kind(symmetric: bool, parts: int) -> None:
    drawings = boss(2, parts, symmetric=symmetric)
    assert 1 <= len(drawings["parts"]) <= parts
    for group in set(drawings["groups"]):
        members = [index for index, each in enumerate(drawings["groups"]) if each == group]
        assert len({id(drawings["parts"][index][0]) for index in members}) == 1
        assert len({drawings["kinds"][index] for index in members}) == 1


def test_a_symmetric_boss_has_its_odd_part_in_the_middle_and_its_pairs_mirrored() -> None:
    for seed in range(5):
        xs = sorted(x for _, x, _ in boss(seed, 3)["parts"])
        assert xs == pytest.approx([-x for x in reversed(xs)])  # each part's mirror image
        if len(xs) % 2:
            assert xs[len(xs) // 2] == pytest.approx(0)


def test_nothing_else_stands_where_a_destroyable_part_does() -> None:
    maker = Maker(random.Random(4), (50, 38), parts=6, forced=True, least_armed=5)
    ship = maker.make()
    for part, spot, _, _ in ship.destroyable:
        assert not any(spot.cell(cell) in ship.cells for cell in part.cells)


def test_a_boss_is_made_like_a_ship_only_bigger() -> None:
    plain = make_ship(random.Random(9), (50, 38))
    with_parts = make_ship(random.Random(9), (50, 38), parts=2, symmetric=plain.symmetric())
    assert plain.placed[0].part == with_parts.placed[0].part  # the same hull, picked the same way


def test_most_ships_are_symmetric_some_lopsided() -> None:
    makers = [Maker(random.Random(seed), (30, 24)) for seed in range(200)]
    for maker in makers:
        maker.make()
        assert maker.ship.symmetric() or not maker.symmetric  # a symmetric ship's cubes mirror each other
    lopsided = [maker for maker in makers if not maker.ship.symmetric()]
    assert 20 < len(lopsided) < 100
    assert set().union(*(maker.lopsided for maker in lopsided)) == set(LOPSIDED)


def test_every_layout_is_made_the_city_like_ones_on_bigger_ships() -> None:
    small = Counter(Maker(random.Random(seed), (22, 22)).layout for seed in range(300))
    assert set(small) == set(LAYOUTS)  # under CITY_FROM square cubes: aircraft only
    big = Counter(Maker(random.Random(seed), (120, 90)).layout for seed in range(300))
    assert set(big) == set(LAYOUTS) | set(CITY_LAYOUTS)
    assert sum(big[layout] for layout in CITY_LAYOUTS) > 150  # most of them
    players = Counter(Maker(random.Random(seed), (18, 18), player=True).layout for seed in range(100))
    assert set(players) == set(PLAYER_LAYOUTS)


def test_ships_are_about_the_size_wanted() -> None:
    for wanted in [(9, 9), (30, 21), (20, 40)]:
        best = min(miss(make_ship(random.Random(seed), wanted).size(), wanted) for seed in range(20))
        assert best < 0.25


def test_a_bigger_ship_is_made_from_more_parts() -> None:
    small = sum(len(make_ship(random.Random(seed), (12, 12)).placed) for seed in range(20))
    big = sum(len(make_ship(random.Random(seed), (50, 40)).placed) for seed in range(20))
    assert big > small


def test_a_tiny_ship_gets_no_part_higher_than_its_hull_allows() -> None:
    for seed in range(60):
        maker = Maker(random.Random(seed), (9, 9))
        maker.make()
        thickness = maker.hull.part.extent()[2]
        for placed in maker.ship.placed[1:]:
            part = placed.part
            if part.kind in ("engine", "hull"):  # engines, pods and booms
                assert part.extent()[2] <= thickness + THICKER
            elif part.kind == "cockpit":
                assert part.extent()[2] <= max(2.0, thickness * COCKPIT_TALL)
            elif part.mount != "wing":
                assert part.extent()[2] <= max(2.0, thickness * TALL)


def test_what_a_ship_gets_once_framed_stays_within_its_frame_but_its_nose_guns() -> None:
    for seed in range(20):
        maker = Maker(random.Random(seed), (40, 30))
        framed = maker.frame().size()
        made = maker.dress().size()
        assert made[0] == framed[0]
        assert framed[1] <= made[1] <= framed[1] + nose_room(30)


@pytest.mark.parametrize("layout", ["multihull", "cluster", "city"])
def test_a_city_like_ship_is_several_hulls_in_one_piece(layout: str) -> None:
    for seed in range(40):
        maker = Maker(random.Random(seed), (120, 90))
        if maker.layout != layout:
            continue
        ship = maker.make()
        assert len(maker.hulls) > 1
        if layout != "city":
            assert any(placed.part.kind == "connector" for placed in ship.placed)  # its hulls joined by beams
            assert len(ship.nozzles) >= 1
        drawing = finish(random.Random(seed), ship)()["core"]
        assert len(pieces(models.parse_voxels(drawing).cells)) == 1  # every cube touching the others
        return
    pytest.fail(f"no {layout} made")


def test_the_hulls_of_a_multihull_or_cluster_ship_get_engines_on_their_tails() -> None:
    for seed in range(30):
        maker = Maker(random.Random(seed), (120, 90))
        if maker.layout not in ("multihull", "cluster"):
            continue
        ship = maker.make()
        tails = {round(at.x) for _, at in maker.hulls}
        flames = {round(x) for x, _, _, _ in ship.nozzles}
        assert len(flames) > len(tails) // 2  # most hulls (not one with another right behind it: no flame through it)


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


def test_a_hull_view_knows_how_wide_it_gets() -> None:
    hull = Hull(of_kind("hull")[10])
    assert hull.broadest == max(half for half, _, _ in hull.part.rows.values())
