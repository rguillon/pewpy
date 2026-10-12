import math

import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.patterns import SWEEP_PERIOD, fire, pattern_angles
from pewpy.game.weapons.guns.state import GunState
from tests.game.weapons.guns.shooting import degrees, shooter


def test_patterns_aim_fan_and_ring() -> None:
    source, target = Entity(x=0, y=0.5), Entity(x=0.5, y=0.0)
    aimed = fire(Gun("aimed", 1, speed=1.0), shooter(source, target))[0]
    assert math.degrees(math.atan2(aimed.vy, aimed.vx)) == pytest.approx(-45)
    fan = fire(Gun("fan", 1, speed=1.0, count=3, spread=30), shooter(source, target))
    assert [round(degrees(b)) for b in fan] == [-30, 0, 30]
    ring = fire(Gun("ring", 1, speed=1.0, count=4, angle=90), shooter(source, target))
    assert sorted(round(degrees(b)) % 360 for b in ring) == [0, 90, 180, 270]


def test_shots_can_have_their_own_directions_speeds_or_velocities() -> None:
    listed = fire(Gun("fan", 1, speed=0.5, angles=(-20, 30), angle=10, speeds=(0.4, 0.6)), shooter())
    assert [round(degrees(b)) for b in listed] == [-10, 40]
    assert [math.hypot(b.vx, b.vy) for b in listed] == pytest.approx([0.4, 0.6])
    straight = fire(Gun("fan", 1, speed=0.0, velocities=((0.5, -0.1), (-0.5, -0.1))), shooter())
    assert [(b.vx, b.vy) for b in straight] == [(0.5, -0.1), (-0.5, -0.1)]


def test_a_gun_fires_from_each_of_its_origins_aiming_from_there() -> None:
    gun = Gun("aimed", 1, speed=1.0, origins=((-0.2, 0.0), (0.2, -0.1)))
    left, right = fire(gun, shooter(Entity(x=0.0, y=0.5), Entity(x=0.2, y=-0.5)))
    assert (left.x, left.y, right.x, right.y) == pytest.approx((-0.2, 0.5, 0.2, 0.4))
    assert right.vx == pytest.approx(0.0, abs=1e-9)  # straight down from its own muzzle to the target


def test_a_shot_turns_with_its_gun_and_its_place_in_the_volley() -> None:
    gun = Gun("fan", 1, speed=0.5, volley_angles=(0, 20))
    state = GunState(cooldown=0.0, turned=5.0, volley_index=1)
    assert [round(degrees(b)) for b in fire(gun, shooter(), state)] == [25]
    assert [round(degrees(b)) for b in fire(gun, shooter(), state, angle=-40)] == [-20]


def test_a_beam_gun_fires_a_beam_from_its_muzzle() -> None:
    (beam,) = fire(Gun("beam", 1, speed=0.0, width=0.04, duration=0.3, origins=((0.0, -0.05),)), shooter())
    assert isinstance(beam, Bullet)
    assert (beam.style, beam.width, beam.life) == ("beam", 0.04, 0.3)
    assert beam.y + beam.height / 2 == pytest.approx(0.45)


@pytest.mark.parametrize("pattern", ["ray", "chain"])
def test_rays_and_chains_are_played_out_by_what_carries_them(pattern: str) -> None:
    assert fire(Gun(pattern, 1, speed=0.0), shooter()) == []


def test_the_player_fires_up_the_screen_at_the_enemies() -> None:
    source = Entity(x=0.0, y=-0.5)
    up = shooter(source, Entity(x=0.0, y=0.5))
    up.forward, up.hostile = 1, False
    (shot,) = fire(Gun("fan", 1, speed=0.5), up)
    assert isinstance(shot, Bullet)
    assert (shot.vx, shot.vy, shot.hostile) == (0.0, 0.5, False)


def test_a_sweeping_fan_swings_from_side_to_side() -> None:
    gun = Gun("fan", 1, speed=0.5, sweep=30.0)
    angles = [
        pattern_angles(gun, Entity(), Entity(), 0.0, age)[0] for age in (0.0, SWEEP_PERIOD / 4, SWEEP_PERIOD * 3 / 4)
    ]
    assert angles == pytest.approx([0.0, 30.0, -30.0])
