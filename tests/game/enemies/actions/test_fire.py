from pewpy.game.enemies.actions.fire import Fire
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import parse_gun
from tests.game.enemies.bodies import StandIn

PLAYER = Entity(x=0.0, y=-0.8)


def test_firing_shoots_its_gun_once() -> None:
    shots = Fire(parse_gun({"pattern": "fan", "count": 3, "interval": 1.0, "speed": 0.5})).do(StandIn(y=0.3), PLAYER)
    assert len(shots) == 3


def test_off_the_screen_it_holds_its_fire_unless_its_gun_fires_anyway() -> None:
    above = StandIn(y=5.0)
    assert Fire(parse_gun({"pattern": "aimed", "interval": 1.0, "speed": 0.5})).do(above, PLAYER) == []
    assert (
        len(
            Fire(parse_gun({"pattern": "aimed", "interval": 1.0, "speed": 0.5, "off_screen": "fire"})).do(above, PLAYER)
        )
        == 1
    )
