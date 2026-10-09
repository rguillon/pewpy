"""The bosses: ships made like any other, bigger, with destroyable parts assembled from the catalog's parts."""

import random

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.palette import GREYS, pick_colors
from pewpy.generators.models.common.palette import palette as make_palette
from pewpy.generators.models.ships.modules import ARMED, KINDS, module
from pewpy.generators.models.ships.placing import Maker, make_ship
from pewpy.generators.models.ships.selection import FLAMES
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


@pytest.mark.parametrize("kind", list(KINDS))
def test_a_module_is_one_symmetric_piece_on_its_base(kind: str) -> None:
    rng = random.Random(kind)
    for size in (1, 2, 3):
        made = module(rng, kind, size)
        assert len(pieces(made.cells)) == 1
        assert made.symmetric
        assert made.low[1:] == (0, 0)
        assert made.extent()[2] <= 14  # standing on a flat platform, its details on the deck
        assert set(made.cells.values()) <= set(COLORS)
        if kind in ARMED:
            assert made.weapons


def test_modules_of_a_kind_vary_and_grow_with_their_size() -> None:
    rng = random.Random(5)
    assert len({frozenset(module(rng, "turret", 2).cells.items()) for _ in range(6)}) > 3
    small = sum(len(module(rng, "cannon", 1).cells) for _ in range(5))
    big = sum(len(module(rng, "cannon", 5).cells) for _ in range(5))
    assert big > small
