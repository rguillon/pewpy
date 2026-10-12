import pytest

from pewpy import config
from pewpy.game.enemies.motions.weave import Weave
from tests.game.enemies.motions.moving import enemy, move


def test_weaving_around_its_column() -> None:
    weaver = enemy(x=0.2)
    xs = []
    for _ in range(120):
        move(weaver, Weave(amplitude=0.25, widen=True, period=2.0))
        xs.append(weaver.x)
    reach = 0.25 * config.WIDTH_SCALE
    assert max(xs) == pytest.approx(0.2 + reach, abs=0.01)
    assert min(xs) == pytest.approx(0.2 - reach, abs=0.01)
    narrow = enemy(x=0.0)
    move(narrow, Weave(amplitude=0.1, period=2.0), 0.5)
    assert narrow.x == pytest.approx(0.1, abs=0.001)
