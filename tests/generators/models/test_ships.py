"""The ships made from the kit's parts: the enemies' and the player's."""

import random

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.ships.kit import ARCHETYPES, PLAYER_ARCHETYPES
from pewpy.generators.models.ships.selection import build, finish
from pewpy.graphics import models


def made(kind: str, seed: int, *, player: bool = False) -> dict:
    rng = random.Random(seed)
    return finish(rng, build(rng, kind, player=player), player=player)()


@pytest.mark.parametrize("kind", list(ARCHETYPES))
def test_every_kind_of_enemy_makes_armed_ships_the_game_can_read(kind: str) -> None:
    for seed in range(40):
        drawing = made(kind, seed)
        voxels = models.parse_voxels(drawing)
        assert len(pieces(voxels.cells)) == 1  # every cube touching the others
        assert drawing["weapons"]
        assert all(engine["towards"] == "top" for engine in drawing["engines"])  # enemies fly down the screen


@pytest.mark.parametrize("kind", list(PLAYER_ARCHETYPES))
def test_the_players_ships_point_up_and_list_no_weapons(kind: str) -> None:
    for seed in range(40):
        drawing = made(kind, seed, player=True)
        assert len(pieces(models.parse_voxels(drawing).cells)) == 1
        assert "weapons" not in drawing
        assert all(engine["towards"] == "bottom" for engine in drawing["engines"])


def test_a_bigger_fit_makes_a_bigger_ship() -> None:
    small = build(random.Random(5), "fighter", fit=0.7).size()
    big = build(random.Random(5), "fighter", fit=1.6).size()
    assert big[0] > small[0]
    assert big[1] > small[1]


@pytest.mark.parametrize("kind", [*ARCHETYPES, *PLAYER_ARCHETYPES])
@pytest.mark.parametrize("fit", [0.3, 2.0, 4.0])
def test_a_ship_can_be_made_much_smaller_or_bigger(kind: str, fit: float) -> None:
    for seed in range(10):
        made = build(random.Random(seed), kind, player=kind in PLAYER_ARCHETYPES, fit=fit)
        assert made.cells
