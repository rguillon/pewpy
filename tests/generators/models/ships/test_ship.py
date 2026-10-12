import random

from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.ships.placing import make_ship
from pewpy.generators.models.ships.ship import Ship, Spot


def test_a_symmetric_ship_keeps_its_axis_in_its_drawings_middle() -> None:
    for seed in range(30):
        ship = make_ship(random.Random(seed), (25, 20))
        if ship.symmetric():
            drawing = ship.drawing({}, 5)["core"]
            assert all(row == row[::-1] for layer in drawing["layers"] for row in layer)


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
