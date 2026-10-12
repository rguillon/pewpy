from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import at
from tests.game.weapons.guns.shooting import shooter


def test_a_gun_can_fire_once_when_its_state_has_some_time_left() -> None:
    gun = Gun("aimed", 0.0, speed=0.5, at=0.8)
    state = GunState(cooldown=0.0)
    assert at.step(gun, state, shooter(remaining=1.0)) == []
    assert len(at.step(gun, state, shooter(remaining=0.8))) == 1
    assert state.fired
    assert at.step(gun, state, shooter(remaining=0.5)) == []
