from pewpy.game.weapons.bullets import BossBeam
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.laser import LASER_WARNING
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import step
from tests.game.weapons.guns.shooting import DT, shooter


def run(gun: Gun, state: GunState, seconds: float, **aim: float) -> list:
    return [shot for _ in range(round(seconds / DT)) for shot in step(gun, state, shooter(**aim), DT)]  # ty: ignore[invalid-argument-type]


def test_a_laser_warns_then_fires_its_beams() -> None:
    state = GunState(cooldown=0.0)
    (warning,) = step(Gun("laser", 5.0, speed=0.0), state, shooter(), DT)
    assert isinstance(warning, BossBeam)
    assert warning.harmless
    beams = run(Gun("laser", 5.0, speed=0.0), state, LASER_WARNING + 2 * DT)
    assert [beam.harmless for beam in beams] == [False]


def test_a_plain_gun_fires_as_soon_as_it_has_reloaded() -> None:
    assert len(step(Gun("fan", 1.0, 0.5), GunState(cooldown=0.0), shooter(), DT)) == 1


def test_a_charged_gun_starts_charging_instead() -> None:
    state = GunState(cooldown=0.0)
    assert step(Gun("fan", 1.0, 0.5, charge=0.5), state, shooter(), DT) == []
    assert state.charging == 0.5


def test_a_gun_firing_at_a_time_of_its_state_waits_for_it() -> None:
    gun = Gun("fan", 1.0, 0.5, at=0.5)
    assert step(gun, GunState(cooldown=0.0), shooter(remaining=0.6), DT) == []
    assert len(step(gun, GunState(cooldown=0.0), shooter(remaining=0.5), DT)) == 1


def test_a_gun_waiting_for_its_volley_starts_it_on_the_next_frame() -> None:
    state = GunState(cooldown=0.0)
    assert step(Gun("fan", 1.0, 0.5, volley=2, wait_volley=True), state, shooter(), DT) == []
    assert state.volley_left == 2


def test_a_gun_with_a_window_fires_only_in_it() -> None:
    gun = Gun("fan", 1.0, 0.5, window=0.1, gap=0.05)
    assert step(gun, GunState(cooldown=0.0), shooter(clock=0.5), DT) == []
    assert len(step(gun, GunState(cooldown=0.0), shooter(clock=1.05), DT)) == 1
