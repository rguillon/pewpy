import pytest

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.weapons.bullets import Bullet
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.shooter import Shooter
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import charge, step
from tests.game.weapons.guns.shooting import BELOW, DT, SOURCE, shooter


def test_a_charging_gun_glows_then_fires_and_its_beam_holds_it_still() -> None:
    stops = []
    aim = Shooter(SOURCE, BELOW, 0.0, 0.0, 0.0, on_screen=True, make=Enemy.of_kind, stop=lambda: stops.append(True))
    gun = Gun("beam", 2.0, speed=0.0, charge=0.5, hold=True, width=0.04, duration=0.3, origins=((0.0, -0.05),))
    state = GunState(cooldown=0.0)
    assert step(gun, state, aim, DT) == []
    assert stops
    assert state.charging > 0
    assert state.busy
    shots: list = []
    for _ in range(round(0.5 / DT) + 1):  # summing 1/60 never lands on 0.5 exactly: one frame more, maybe
        shots += step(gun, state, aim, DT)
    assert len(shots) == 1
    beam = shots[0]
    assert isinstance(beam, Bullet)
    assert beam.style == "beam"
    assert beam.pierces
    assert beam.width == 0.04
    assert beam.y + beam.height / 2 == pytest.approx(0.45)  # from the muzzle down
    assert state.beaming > 0
    for _ in range(round(0.3 / DT) + 1):
        assert step(gun, state, aim, DT) == []
    step(gun, state, aim, DT)
    assert not state.busy


def test_a_charged_gun_that_isnt_a_beam_fires_its_pattern_once_charged() -> None:
    gun = Gun("fan", 1.0, speed=0.5, count=3, charge=0.2)
    state = GunState(cooldown=0.0, charging=0.2)
    assert charge.step(gun, state, shooter(), 0.1) == []
    assert len(charge.step(gun, state, shooter(), 0.1)) == 3
    assert state.beaming == 0
