"""Ships and bosses made to a size."""

import random

import pytest

from pewpy.generators.models import sized
from pewpy.generators.models.sized import MAX_PARTS, MIN_PARTS, cubes, miss, parts_for, rounded, sized_boss, sized_ship


def drawn(drawing: dict) -> tuple[int, int]:
    layer = drawing["layers"][0]
    return len(layer[0]), len(layer)


@pytest.mark.parametrize(("size", "player"), [((0.12, 0.12), True), ((0.06, 0.06), False), ((0.2, 0.14), False)])
def test_a_ship_is_made_about_the_size_asked(size: tuple[float, float], player: bool) -> None:
    drawing = sized_ship(random.Random(4), size, player=player)
    assert drawing["size"] == rounded(size)
    assert miss(drawn(drawing), cubes(size)) < 0.3


def test_a_boss_core_is_made_about_the_size_asked() -> None:
    made = sized_boss(random.Random(1), (0.3, 0.2))
    assert made["core"]["size"] == [0.3, 0.2]
    assert miss(drawn(made["core"]), cubes((0.3, 0.2))) < 0.3
    assert len(made["parts"]) == parts_for((0.3, 0.2))


def test_bigger_bosses_have_more_parts_in_pairs() -> None:
    counts = [parts_for((width, width * 0.7)) for width in (0.1, 0.3, 0.5, 0.7, 2.0)]
    assert counts == sorted(counts)
    assert counts[0] == MIN_PARTS
    assert counts[-1] == MAX_PARTS
    assert all(count % 2 == 0 for count in counts)


def test_a_boss_that_cant_be_made_says_so(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sized, "boss", lambda *_: None)
    with pytest.raises(ValueError, match="no boss"):
        sized_boss(random.Random(1), (0.01, 0.01))


def test_the_nearer_size_misses_less() -> None:
    assert miss((10, 10), (10, 10)) == 0
    assert miss((11, 10), (10, 10)) < miss((14, 10), (10, 10))
    assert miss((9, 10), (10, 10)) > 0
