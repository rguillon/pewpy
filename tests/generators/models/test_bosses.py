"""The bosses: a core sculpted from a plan, with its parts."""

import random

import pytest

from pewpy.generators.models.bosses.greebles import ON_TOP, _on_top
from pewpy.generators.models.bosses.modules import ARMED, KINDS, module
from pewpy.generators.models.bosses.mounting import part
from pewpy.generators.models.bosses.selection import boss
from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.palette import CORE_GREYS, PART_GREYS, pick_colors
from pewpy.generators.models.common.palette import palette as make_palette
from pewpy.generators.models.parts import of_kind
from pewpy.graphics import models

MIN_WEAPONS = 5


def weapons_of(drawings: dict) -> int:
    return len(drawings["core"]["weapons"]) + sum(
        len(drawing.get("weapons", [])) for drawing, _, _ in drawings["parts"]
    )


def test_bosses_are_drawings_the_game_can_read_armed_with_their_parts() -> None:
    rng = random.Random(11)
    bosses = [made.make() for made in (boss(rng, lopsided=seed % 5 == 0) for seed in range(40)) if made is not None]
    assert len(bosses) > 30
    for drawings in bosses:
        for drawing in [drawings["core"], *(drawing for drawing, _, _ in drawings["parts"])]:
            assert len(pieces(models.parse_voxels(drawing).cells)) == 1  # every cube touching the others
        assert weapons_of(drawings) >= MIN_WEAPONS
        assert len(drawings["groups"]) == len(drawings["parts"])


@pytest.mark.parametrize(("lopsided", "wanted"), [(False, 4), (False, 5), (True, 3), (False, 0)])
def test_a_boss_can_be_asked_for_a_size_and_a_number_of_parts(lopsided: bool, wanted: int) -> None:
    made = boss(random.Random(2), lopsided=lopsided, cubes=(61, 41), parts_wanted=wanted)
    assert made is not None
    drawings = made.make()
    assert len(drawings["core"]["layers"][0][0]) <= 61
    assert len(drawings["parts"]) == len(drawings["groups"]) == len(drawings["kinds"]) == wanted
    for group in set(drawings["groups"]):  # a group's parts share their drawing and kind
        members = [index for index, each in enumerate(drawings["groups"]) if each == group]
        assert len({id(drawings["parts"][index][0]) for index in members}) == 1
        assert len({drawings["kinds"][index] for index in members}) == 1


def test_a_symmetric_boss_has_its_odd_part_in_the_middle() -> None:
    made = boss(random.Random(5), lopsided=False, cubes=(61, 41), parts_wanted=3)
    assert made is not None
    xs = sorted(x for _, x, _ in made.make()["parts"])
    assert xs[0] == pytest.approx(-xs[2])
    assert xs[1] == pytest.approx(0)


def test_a_core_too_small_makes_no_boss() -> None:
    assert boss(random.Random(1), lopsided=False, cubes=(9, 9)) is None


def test_parts_without_room_go_in_the_middle() -> None:
    made = boss(random.Random(3), lopsided=False, cubes=(41, 31), parts_wanted=30)  # more than it has room for
    assert made is not None
    parts = made.make()["parts"]
    assert len(parts) == 30
    assert any(x == pytest.approx(0) for _, x, _ in parts)


def test_a_wide_lopsided_boss_has_no_piece_floating_by_its_side() -> None:
    for seed in range(4):
        made = boss(random.Random(seed), lopsided=True, cubes=(111, 77), parts_wanted=6)
        assert made is not None
        assert len(pieces(models.parse_voxels(made.make()["core"]).cells)) == 1


def test_the_catalogs_parts_a_boss_carries_are_all_colored_by_its_palettes() -> None:
    colors = pick_colors(random.Random(0))
    stamped = [*_on_top(ON_TOP), *_on_top(("gun", "missile")), *of_kind("engine", "tail")]
    assert {char for piece in stamped for char in piece.cells.values()} <= set(make_palette(CORE_GREYS, colors))


def test_a_destroyable_part_is_a_symmetric_module_of_parts_bigger_on_a_wider_boss() -> None:
    rng = random.Random(3)
    for kind in KINDS:
        small, big = part(rng, kind, 10), part(rng, kind, 400)
        assert small.kind == big.kind == "module"
        assert small.name.startswith("small")
        assert kind in small.name
        assert big.name.startswith("colossal")  # the biggest size
        assert len(big.cells) > len(small.cells)


@pytest.mark.parametrize("kind", list(KINDS))
def test_a_module_is_one_symmetric_piece_on_its_base_round_its_main_piece(kind: str) -> None:
    rng = random.Random(kind)
    for size in (1, 2, 3):
        made = module(rng, kind, size)
        assert len(pieces(made.cells)) == 1
        assert made.symmetric
        assert made.low[1:] == (0, 0)
        assert made.extent()[2] <= 14  # standing on a flat platform, its details on the deck
        assert set(made.cells.values()) <= set(make_palette(PART_GREYS, pick_colors(rng)))
        assert bool(made.weapons) == (kind in ARMED) or made.weapons  # armed kinds always, others maybe (nose guns)


def test_modules_of_a_kind_vary() -> None:
    rng = random.Random(5)
    assert len({frozenset(module(rng, "turret", 2).cells.items()) for _ in range(6)}) > 3
