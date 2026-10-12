import random

from pewpy.generators.models.ships.paint import livery, markings, nose_cone, wing_stripes
from pewpy.generators.models.ships.ship import Ship


def plain_ship() -> Ship:
    """Make a flat hull 3 wide and 10 long, with wings 4 cubes out on each side."""
    ship = Ship()
    for y in range(10):
        for x in range(-1, 2):
            ship.cells[x, y, 0] = "h"
            ship.tops[x, y] = 0
    for y in range(3, 6):
        for x in (*range(-5, -1), *range(2, 6)):
            ship.cells[x, y, 0] = "w"
            ship.tops[x, y] = 0
    return ship


def test_the_livery_is_a_stripe_across_the_top() -> None:
    ship = plain_ship()
    livery(random.Random(0), ship, 10)
    striped = {y for (_, y, _), char in ship.cells.items() if char == "L"}
    assert 1 <= len(striped) <= 2
    assert all(3 <= y <= 7 for y in striped)
    assert all(ship.cells[x, y, 0] == "L" for x in range(-1, 2) for y in striped)


def test_the_nose_cone_is_the_hulls_last_rows_in_the_accent() -> None:
    ship = plain_ship()
    nose_cone(random.Random(0), ship, 10, 1)
    painted = {y for (_, y, _), char in ship.cells.items() if char == "p"}
    assert painted == set(range(min(painted), 10))
    assert 2 <= len(painted) <= 4


def test_wing_stripes_run_along_the_wings_only() -> None:
    ship = plain_ship()
    wing_stripes(random.Random(0), ship)
    assert all(abs(x) > 1 for (x, _, _), char in ship.cells.items() if char == "L")
    assert any(char == "L" for char in ship.cells.values())
    bare = Ship(cells={(0, 0, 0): "h"})
    wing_stripes(random.Random(0), bare)
    assert bare.cells == {(0, 0, 0): "h"}


def test_markings_are_on_both_wing_tips() -> None:
    ship = plain_ship()
    markings(random.Random(0), ship)
    marked = [x for (x, _, _), char in ship.cells.items() if char == "q"]
    assert min(marked) <= -4
    assert max(marked) >= 4
    assert all(abs(x) >= 3 for x in marked)
    lone = Ship(cells={(0, 0, 0): "h"})
    markings(random.Random(0), lone)
    assert "q" not in lone.cells.values()
