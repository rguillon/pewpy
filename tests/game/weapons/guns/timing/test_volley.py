import math
from dataclasses import replace

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.timing import step
from pewpy.game.weapons.guns.timing.volley import reloaded, shoot, start_volley, volley
from tests.game.weapons.guns.shooting import DT, degrees, frames, shooter


def test_reloading_counts_again_from_the_shot_or_carries_what_it_was_late_by() -> None:
    reset = frames(Gun("fan", 0.105, speed=0.5), 1.0)
    carry = frames(Gun("fan", 0.105, speed=0.5, reload="carry"), 1.0)
    assert reset[1] - reset[0] == 7  # 0.105 s is 6.3 frames: the 7th
    assert len(carry) > len(reset)  # on average, one every 6.3 frames


def test_a_clamped_wait_doesnt_make_up_for_lost_time() -> None:
    state = GunState(cooldown=0.0)
    assert reloaded(Gun("fan", 1.0, 0.5, reload="clamp"), state, shooter(), 0.5)
    assert state.cooldown == 1.0


def test_with_the_trigger_released_the_gun_waits_ready() -> None:
    aim = shooter()
    aim.trigger = False
    state = GunState(cooldown=0.1)
    assert not reloaded(Gun("fan", 1.0, 0.5), state, aim, 0.5)
    assert state.cooldown == 0.0


def test_off_screen_a_shot_waits_is_skipped_or_fires() -> None:
    gun = Gun("fan", 1.0, speed=0.5)
    hidden = shooter(on_screen=False)
    assert frames(gun, 2.0, hidden) == []
    held = GunState(cooldown=0.0)
    frames(gun, 2.0, hidden, held)
    assert step(gun, held, shooter(), DT)  # fires as soon as it's on screen
    skipped = GunState(cooldown=0.0)
    frames(replace(gun, off_screen="skip"), 0.5, hidden, skipped)
    assert skipped.cooldown > 0  # its shot went by: the next one waits
    assert frames(replace(gun, off_screen="fire"), 2.0, hidden) == [0, 60]


def test_a_gun_can_fire_only_when_lined_up_with_the_player() -> None:
    gun = Gun("fan", 0.5, speed=0.5, aligned=0.06)
    assert frames(gun, 1.0, shooter(target=Entity(x=0.3, y=-0.8))) == []
    assert len(frames(gun, 1.0, shooter(target=Entity(x=0.05, y=-0.8)))) == 2


def test_a_gun_needing_a_target_waits_for_one() -> None:
    aim = shooter()
    aim.target = None
    assert not reloaded(Gun("fan", 1.0, 0.5, needs_target=True), GunState(cooldown=0.0), aim, DT)


def test_a_volleys_shots_can_turn_one_by_one() -> None:
    gun = Gun("fan", 0.5, speed=0.5, volley=3, gap=0.1, volley_angles=(0, 30, 60))
    state = GunState(cooldown=0.0)
    shots = [shot for _ in range(30) for shot in step(gun, state, shooter(), DT)]
    assert [round(degrees(shot)) for shot in shots] == [0, 30, 60]
    assert state.volleys == 1
    assert not state.busy


def test_a_sequence_takes_turns() -> None:
    gun = Gun("fan", 0.5, speed=0.0, sequence=(Gun("fan", 0, speed=0.5, angle=-10), Gun("fan", 0, speed=0.5, angle=10)))
    state = GunState(cooldown=0.0)
    shots = [shot for _ in range(round(1.6 / DT)) for shot in step(gun, state, shooter(), DT)]
    assert [round(degrees(shot)) for shot in shots] == [-10, 10, -10, 10]


def test_a_volley_starts_with_its_first_shot_at_once_then_one_every_gap() -> None:
    gun = Gun("fan", 1.0, 0.5, volley=2, gap=0.1)
    state = GunState(cooldown=0.0)
    assert start_volley(gun, state) is gun
    assert (state.volley_left, state.shots) == (2, 1)
    assert len(volley(state, shooter(), DT)) == 1
    assert volley(state, shooter(), 0.05) == []
    assert len(volley(state, shooter(), 0.05)) == 1
    assert (state.volley_left, state.volleys) == (0, 1)
    assert volley(state, shooter(), 1.0) == []


def test_each_shot_of_a_turning_gun_turns_the_next() -> None:
    gun = Gun("fan", 1.0, 0.5, turn=10.0)
    state = GunState(cooldown=0.0, volley_left=1)
    shoot(gun, state, shooter())
    assert (state.turned, state.volley_index) == (10.0, 1)
    assert math.isclose(degrees(shoot(gun, state, shooter())[0]), 10.0)
