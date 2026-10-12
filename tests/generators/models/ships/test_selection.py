import random

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.ships.placing import make_ship
from pewpy.generators.models.ships.selection import build, finish
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


def test_a_bigger_ship_has_more_engines_and_longer_flames() -> None:
    def engines(wanted: tuple[float, float]) -> float:
        return sum(len(make_ship(random.Random(seed), wanted).nozzles) for seed in range(8)) / 8

    assert engines((15, 15)) < engines((60, 45)) < engines((120, 90))
    short = finish(random.Random(1), make_ship(random.Random(1), (20, 20)))()["core"]
    long = finish(random.Random(1), make_ship(random.Random(1), (120, 90)))()["core"]
    assert max(engine["length"] for engine in long["engines"]) > max(engine["length"] for engine in short["engines"])
