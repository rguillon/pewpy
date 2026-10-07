"""How hard each level is, and what that sets."""

import pytest

from pewpy.tools.levels.difficulty import MAX_DIFFICULTY, SCROLL_SPEED, THREAT, between, budget, difficulty


def test_a_worlds_first_level_is_as_hard_as_the_third_of_the_world_before() -> None:
    assert difficulty(1, 1) == 1
    assert difficulty(1, 6) == 6
    assert difficulty(2, 1) == difficulty(1, 3)
    assert difficulty(8, 6) == MAX_DIFFICULTY


def test_values_go_from_the_easiest_to_the_hardest_level() -> None:
    assert between(SCROLL_SPEED, 1) == SCROLL_SPEED[0]
    assert between(SCROLL_SPEED, MAX_DIFFICULTY) == pytest.approx(SCROLL_SPEED[1])
    assert SCROLL_SPEED[0] < between(SCROLL_SPEED, 10) < SCROLL_SPEED[1]


def test_the_threat_rises_fast_at_first_then_slower_and_keeps_growing() -> None:
    assert budget(1) == THREAT[0]
    assert budget(MAX_DIFFICULTY) == pytest.approx(THREAT[1])
    steps = [budget(d + 1) - budget(d) for d in range(1, MAX_DIFFICULTY)]
    assert all(step > 0 for step in steps)
    assert steps == sorted(steps, reverse=True)  # each step smaller than the one before
    assert budget(MAX_DIFFICULTY + 2) > budget(MAX_DIFFICULTY)  # a harder second half on the hardest level
