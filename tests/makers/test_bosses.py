"""The bosses: a core sculpted from a plan, with its parts."""

import random

import pytest

from pewpy.graphics import models
from pewpy.makers.bosses.selection import boss
from pewpy.makers.common.connect import pieces

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
