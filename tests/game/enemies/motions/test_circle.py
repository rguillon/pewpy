import math

import pytest

from pewpy.game.enemies.motions.circle import Circle
from tests.game.enemies.motions.moving import enemy, move


def test_circling_while_coming_down() -> None:
    mite = enemy(y=0.5)
    move(mite, Circle(radius=0.12, turn=3.0, descent=0.2), 2 * math.pi / 3.0)
    assert mite.x == pytest.approx(0.0, abs=0.01)  # a full turn
    assert mite.y == pytest.approx(0.5 - 0.2 * 2 * math.pi / 3.0, abs=0.01)
