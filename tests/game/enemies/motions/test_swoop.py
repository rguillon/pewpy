from pewpy.game.enemies.motions.swoop import Swoop
from tests.game.enemies.motions.moving import enemy, move


def test_swooping_down_then_up() -> None:
    swooper = enemy()
    move(swooper, Swoop(amplitude=-0.5, rate=1.2))
    assert swooper.vy < 0
    move(swooper, Swoop(amplitude=-0.5, rate=1.2), 2.0)
    assert swooper.vy > 0
