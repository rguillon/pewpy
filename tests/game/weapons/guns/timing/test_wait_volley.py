from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import wait_volley
from tests.game.weapons.guns.shooting import DT, shooter


def test_a_gun_waiting_for_its_volley_doesnt_reload_meanwhile() -> None:
    gun = Gun(
        "fan", 0.5, speed=0.5, wait_volley=True,
        sequence=(Gun("fan", 0.0, speed=0.5, volley=3, gap=0.1), Gun("fan", 0.0, speed=0.5, count=2)),
    )  # fmt: skip
    state = GunState(cooldown=0.0)
    assert wait_volley.step(gun, state, shooter(), DT) == []  # the volley starts on the next frame
    shots = [len(wait_volley.step(gun, state, shooter(), DT)) for _ in range(round(1.0 / DT))]
    assert [count for count in shots if count] == [1, 1, 1, 2]  # three in a row, then a pair at once
    assert shots.index(2) > round((0.2 + 0.5) / DT)  # reloading started again after the volley


def test_a_volley_of_one_fires_at_once() -> None:
    state = GunState(cooldown=0.0)
    assert len(wait_volley.step(Gun("fan", 0.5, speed=0.5, wait_volley=True), state, shooter(), DT)) == 1
    assert (state.volley_left, state.volleys) == (0, 1)
    assert wait_volley.step(Gun("fan", 0.5, speed=0.5, wait_volley=True), state, shooter(), DT) == []
