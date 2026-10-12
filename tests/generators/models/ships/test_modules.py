import random

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.palette import GREYS, pick_colors
from pewpy.generators.models.common.palette import palette as make_palette
from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.ships import modules
from pewpy.generators.models.ships.modules import ARMED, KINDS, _flat, _nose_guns, module
from pewpy.generators.models.ships.ship import Ship, Spot

COLORS = make_palette(GREYS, pick_colors(random.Random(0)))


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


def never(*_args: object, **_kwargs: object) -> bool:
    return False


def test_a_module_whose_front_guns_fit_nowhere_goes_without(monkeypatch: pytest.MonkeyPatch) -> None:
    ship = Ship()
    platform = _flat(of_kind("hull")[20])
    ship.place(platform, [Spot(0, 0, 0)])
    monkeypatch.setattr(modules, "_put", never)
    _nose_guns(random.Random(1), ship, platform)
    assert len(ship.placed) == 1
