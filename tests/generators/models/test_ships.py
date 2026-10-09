"""The ships made from the catalog's parts: the enemies' and the player's."""

import random
from collections import Counter

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.ships.placing import (
    COCKPIT_TALL,
    LAYOUTS,
    LOPSIDED,
    PLAYER_LAYOUTS,
    TALL,
    THICKER,
    Maker,
    make_ship,
    miss,
)
from pewpy.generators.models.ships.selection import build, finish
from pewpy.generators.models.ships.ship import Ship, Spot
from pewpy.graphics import models

SIZES = [(9, 9), (18, 18), (30, 21), (50, 30), (15, 45), (60, 15)]


def made(seed: int, wanted: tuple[float, float], *, player: bool = False) -> dict:
    rng = random.Random(seed)
    return finish(rng, build(rng, wanted, player=player), player=player)()


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
            drawing = ship.drawing({}, 5)
            assert all(row == row[::-1] for layer in drawing["layers"] for row in layer)


def test_every_layout_is_made() -> None:
    layouts = Counter(Maker(random.Random(seed), (30, 24)).layout for seed in range(300))
    assert set(layouts) == set(LAYOUTS)
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
