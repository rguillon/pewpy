import math

import pytest

from pewpy.game.enemies.motions.erratic import Erratic
from tests.game.enemies.motions.moving import enemy, move


def test_drifting_erratically() -> None:
    scrapper = enemy(x=0.1)
    move(scrapper, Erratic(every=0.5, speed=0.25, a=2.4, b=7.0))
    first = scrapper.vx
    assert first == pytest.approx(0.25 * math.sin(2.4 + 0.1 * 7.0))
    move(scrapper, Erratic(every=0.5, speed=0.25, a=2.4, b=7.0), 0.4)
    assert scrapper.vx == first  # holds its course half a second
