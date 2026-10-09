"""The ships made from the catalog's parts: the enemies' and the player's."""

import random
from collections import Counter

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.geometry import miss
from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.ships.placing import (
    CITY_LAYOUTS,
    COCKPIT_TALL,
    LAYOUTS,
    LOPSIDED,
    PLAYER_LAYOUTS,
    TALL,
    THICKER,
    Maker,
    make_ship,
    nose_room,
)
from pewpy.generators.models.ships.selection import Asked, build, finish
from pewpy.generators.models.ships.ship import Ship, Spot
from pewpy.generators.models.sized import _aimed
from pewpy.graphics import models

SIZES = [(9, 9), (18, 18), (30, 21), (50, 30), (15, 45), (60, 15)]


def made(seed: int, wanted: tuple[float, float], *, player: bool = False) -> dict:
    rng = random.Random(seed)
    return finish(rng, build(rng, wanted, player=player), player=player)()["core"]


@pytest.mark.parametrize("wanted", SIZES)
def test_enemies_are_armed_in_one_piece_and_fly_down_the_screen(wanted: tuple[float, float]) -> None:
    for seed in range(15):
        drawing = made(seed, wanted)
        voxels = models.parse_voxels(drawing)
        assert len(pieces(voxels.cells)) == 1  # every cube touching the others
        assert drawing["weapons"]
        assert drawing["engines"]
        assert all(engine["towards"] == "top" for engine in drawing["engines"])  # enemies fly down the screen


@pytest.mark.parametrize("wanted", SIZES[:4])
def test_the_players_ships_point_up_and_list_no_weapons(wanted: tuple[float, float]) -> None:
    for seed in range(10):
        drawing = made(seed, wanted, player=True)
        assert len(pieces(models.parse_voxels(drawing).cells)) == 1
        assert "weapons" not in drawing
        assert drawing["engines"]
        assert all(engine["towards"] == "bottom" for engine in drawing["engines"])


def test_most_ships_are_symmetric_some_lopsided() -> None:
    makers = [Maker(random.Random(seed), (30, 24)) for seed in range(200)]
    for maker in makers:
        maker.make()
        assert maker.ship.symmetric() or not maker.symmetric  # a symmetric ship's cubes mirror each other
    lopsided = [maker for maker in makers if not maker.ship.symmetric()]
    assert 20 < len(lopsided) < 100
    assert set().union(*(maker.lopsided for maker in lopsided)) == set(LOPSIDED)


def test_a_symmetric_ship_keeps_its_axis_in_its_drawings_middle() -> None:
    for seed in range(30):
        ship = make_ship(random.Random(seed), (25, 20))
        if ship.symmetric():
            drawing = ship.drawing({}, 5)["core"]
            assert all(row == row[::-1] for layer in drawing["layers"] for row in layer)


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


def test_a_part_doesnt_fit_inside_another_nor_in_front_of_a_barrel_nor_behind_a_nozzle() -> None:
    ship = Ship()
    barrel = of_kind("gun", "nose")[0]
    nozzle = of_kind("engine", "tail")[0]
    vent = of_kind("vent")[0]
    ship.place(barrel, [Spot(0, 0, 0)])
    ship.place(nozzle, [Spot(10, 0, 0)])
    assert not ship.fits(vent, [Spot(0, -1, 0)])  # sinking into the barrel
    assert ship.fits(vent, [Spot(0, -1, 0)], overlap=1.0)
    assert not ship.fits(vent, [Spot(0, barrel.high[1] + 1, 0)])  # in front of its tip
    assert not ship.fits(vent, [Spot(10, -10, 0)])  # behind the nozzle
    assert ship.fits(vent, [Spot(0, -10, 0)])
    assert not ship.fits(barrel, [Spot(10, -10, 0)])  # its barrel stuck in the nozzle's housing


def test_a_flipped_spot_mirrors_a_part() -> None:
    ship = Ship()
    wing = of_kind("wing")[0]
    ship.place(wing, [Spot(-1, 0, 0), Spot(1, 0, 0, flip=True)])
    assert ship.symmetric()
    assert min(x for x, _, _ in ship.cells) == -1 + wing.low[0]


def test_what_a_ship_gets_once_framed_stays_within_its_frame_but_its_nose_guns() -> None:
    for seed in range(20):
        maker = Maker(random.Random(seed), (40, 30))
        framed = maker.frame().size()
        made = maker.dress().size()
        assert made[0] == framed[0]
        assert framed[1] <= made[1] <= framed[1] + nose_room(30)


def test_the_frame_is_aimed_at_the_size() -> None:
    for wanted in [(40, 30), (120, 90)]:
        framed = (wanted[0], wanted[1] - nose_room(wanted[1]))
        sizes = [_aimed(seed, wanted, framed, player=False, asked=Asked()).ship.size() for seed in range(6)]
        assert min(miss(size, framed) for size in sizes) < 0.1


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


def test_a_bigger_ship_has_more_engines_and_longer_flames() -> None:
    def engines(wanted: tuple[float, float]) -> float:
        return sum(len(make_ship(random.Random(seed), wanted).nozzles) for seed in range(8)) / 8

    assert engines((15, 15)) < engines((60, 45)) < engines((120, 90))
    short = finish(random.Random(1), make_ship(random.Random(1), (20, 20)))()["core"]
    long = finish(random.Random(1), make_ship(random.Random(1), (120, 90)))()["core"]
    assert max(engine["length"] for engine in long["engines"]) > max(engine["length"] for engine in short["engines"])


def test_the_hulls_of_a_multihull_or_cluster_ship_get_engines_on_their_tails() -> None:
    for seed in range(30):
        maker = Maker(random.Random(seed), (120, 90))
        if maker.layout not in ("multihull", "cluster"):
            continue
        ship = maker.make()
        tails = {round(at.x) for _, at in maker.hulls}
        flames = {round(x) for x, _, _, _ in ship.nozzles}
        assert len(flames) > len(tails) // 2  # most hulls (not one with another right behind it: no flame through it)
