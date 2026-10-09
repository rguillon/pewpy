"""Models made to a size: the player's ships, the enemies and the bosses, all the same way."""

import random

import pytest

from pewpy.generators.models.common.geometry import miss
from pewpy.generators.models.sized import (
    MAX_PARTS,
    MIN_PARTS,
    MIN_WEAPONS,
    PARTS_ALWAYS,
    PARTS_FROM,
    cubes,
    parts_chance,
    parts_for,
    rounded,
    sized_model,
)


def drawn(drawing: dict) -> tuple[int, int]:
    layer = drawing["layers"][0]
    return len(layer[0]), len(layer)


@pytest.mark.parametrize(("size", "player"), [((0.12, 0.12), True), ((0.06, 0.06), False), ((0.2, 0.14), False)])
def test_a_ship_is_made_about_the_size_asked(size: tuple[float, float], player: bool) -> None:
    drawing = sized_model(random.Random(4), size, player=player)["core"]
    assert drawing["size"] == rounded(size)
    assert miss(drawn(drawing), cubes(size)) < 0.3


def test_a_boss_core_is_made_about_the_size_asked() -> None:
    made = sized_model(random.Random(1), (0.3, 0.2), boss=True)
    assert made["core"]["size"] == [0.3, 0.2]
    assert miss(drawn(made["core"]), cubes((0.3, 0.2))) < 0.3
    assert 1 <= len(made["parts"]) <= parts_for((0.3, 0.2))
    weapons = len(made["core"]["weapons"]) + sum(len(drawing.get("weapons", [])) for drawing, _, _ in made["parts"])
    assert weapons >= MIN_WEAPONS


def test_bigger_bosses_have_more_parts_in_pairs() -> None:
    counts = [parts_for((width, width * 0.7)) for width in (0.1, 0.3, 0.5, 0.7, 2.0)]
    assert counts == sorted(counts)
    assert counts[0] == MIN_PARTS
    assert counts[-1] == MAX_PARTS
    assert all(count % 2 == 0 for count in counts)


def test_the_nearer_size_misses_less() -> None:
    assert miss((10, 10), (10, 10)) == 0
    assert miss((11, 10), (10, 10)) < miss((14, 10), (10, 10))
    assert miss((9, 10), (10, 10)) > 0


@pytest.mark.parametrize("size", [(0.5, 0.3), (0.8, 0.6), (1.1, 1.0)])
def test_a_big_boss_is_made_about_the_size_asked(size: tuple[float, float]) -> None:
    made = sized_model(random.Random(3), size, boss=True)
    assert miss(drawn(made["core"]), cubes(size)) < 0.15


def test_the_size_alone_sets_the_chance_of_destroyable_parts() -> None:
    cube = cubes((1.0, 1.0))[0]
    side = (PARTS_FROM + PARTS_ALWAYS) / 2  # half way in area
    assert parts_chance((10 / cube, 10 / cube)) == 0  # 100 square cubes: never
    assert parts_chance((side**0.5 / cube, side**0.5 / cube)) == pytest.approx(0.5)
    assert parts_chance((40 / cube, 40 / cube)) == 1  # 1600: always
    sizes = [(0.1, 0.1), (0.17, 0.17), (0.27, 0.27)]  # 225, 650 and 1640 square cubes
    shares = [sum(bool(sized_model(random.Random(seed), size)["parts"]) for seed in range(12)) for size in sizes]
    assert shares == sorted(shares)
    assert shares[-1] == 12


def test_the_players_ships_never_have_destroyable_parts_and_bosses_always_do() -> None:
    for seed in range(4):
        assert not sized_model(random.Random(seed), (0.3, 0.25), player=True)["parts"]
        assert sized_model(random.Random(seed), (0.1, 0.1), boss=True)["parts"]
