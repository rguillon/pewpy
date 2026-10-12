from pewpy.game.enemies.actions.die import Die
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_dying_takes_the_enemy_away() -> None:
    body = StandIn()
    assert Die().do(body, Entity()) == []
    assert not body.alive
