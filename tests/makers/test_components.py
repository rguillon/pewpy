"""The built-in parts stamped on ships and bosses."""

import random

import pytest

from pewpy.makers.common.connect import pieces
from pewpy.makers.components import COMPONENTS, DETAILS, PART_COMPONENTS, WEAPONS, Piece


@pytest.mark.parametrize("name", list(COMPONENTS))
@pytest.mark.parametrize("size", [1, 2, 3])
def test_every_part_is_symmetric_sits_on_its_base_and_grows_with_its_size(name: str, size: int) -> None:
    for seed in range(4):
        piece = COMPONENTS[name](random.Random(seed), size)
        assert all(piece.cells.get((-x, y, z)) == char for (x, y, z), char in piece.cells.items())
        assert min(z for _, _, z in piece.cells) == 0
        assert min(y for _, y in piece.footprint()) == 0  # its back on row 0
        assert set(piece.cells.values()) <= set("NhHSkrWopGR")  # characters every palette has
    small = COMPONENTS[name](random.Random(0), 1)
    big = COMPONENTS[name](random.Random(0), 3)
    assert len(big.cells) > len(small.cells)


@pytest.mark.parametrize("name", list(WEAPONS))
def test_a_gun_has_weapons_at_its_barrels_tips_in_front(name: str) -> None:
    for seed in range(6):
        piece = COMPONENTS[name](random.Random(seed), 2)
        assert piece.weapons
        front = max(y for _, y in piece.footprint())
        for _, x, y, z in piece.weapons:
            assert y == front  # nothing of it further forward
            assert (x, y, z) in piece.cells
        assert sorted(x for _, x, _, _ in piece.weapons) == sorted(-x for _, x, _, _ in piece.weapons)


def test_an_engine_has_a_nozzle_on_its_back() -> None:
    piece = COMPONENTS["engine"](random.Random(1), 2)
    ((x, y, z, width),) = piece.nozzles
    assert (x, y) == (0, 0)
    assert piece.cells[0, 0, round(z)] == "o"
    assert width > 1


def test_details_are_not_armed() -> None:
    for name in DETAILS:
        piece = COMPONENTS[name](random.Random(1), 2)
        assert not piece.weapons
        assert not piece.nozzles


def test_a_bosss_parts_are_guns_or_machinery() -> None:
    assert set(PART_COMPONENTS) <= set(COMPONENTS)
    assert "engine" not in PART_COMPONENTS


def test_a_piece_draws_mirrored_boxes() -> None:
    piece = Piece()
    piece.box(1, 2, 0, 0, 0, 0, "N")
    piece.housing(0, 0, 4, 1, 1)  # a housing one cube wide: no inner plate
    assert {(x, y) for x, y, z in piece.cells if z == 0} == {(-2, 0), (-1, 0), (1, 0), (2, 0)}
    assert piece.height() == 2


@pytest.mark.parametrize("name", PART_COMPONENTS)
def test_a_bosss_part_is_one_piece(name: str) -> None:
    for size in (1, 2, 4):
        assert len(pieces(COMPONENTS[name](random.Random(size), size).cells)) == 1
