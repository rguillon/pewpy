from pewpy.game.enemies.exits.idle import Idle
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import GunState
from tests.game.enemies.bodies import StandIn


def test_it_holds_while_no_gun_is_busy() -> None:
    assert Idle().holds(StandIn(), Entity())
    assert Idle().holds(StandIn(guns=[GunState(cooldown=1.0)]), Entity())
    for busy in (GunState(0.0, volley_left=2), GunState(0.0, charging=0.5), GunState(0.0, beaming=0.5)):
        assert not Idle().holds(StandIn(guns=[GunState(cooldown=1.0), busy]), Entity())
