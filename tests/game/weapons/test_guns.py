import math
from dataclasses import replace

import pytest

from pewpy import config
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.mounts import Mount
from pewpy.game.entities import Entity
from pewpy.game.weapons import guns
from pewpy.game.weapons.bullets import Bullet
from pewpy.game.weapons.guns import HEAVY_BULLET_SIZE, Gun, GunState, NoMakerError, Shooter, distance, fire, step

DT = 1 / 60
BELOW = Entity(x=0.0, y=-0.8)  # a target straight down the screen
SOURCE = Entity(x=0.0, y=0.5)


def shooter(
    piece: Entity = SOURCE, target: Entity = BELOW, on_screen: bool = True, clock: float = 0.0, remaining: float = 0.0
) -> Shooter:
    return Shooter(piece, target, 0.0, clock, remaining, on_screen, Enemy.of_kind)


def degrees(bullet: Entity) -> float:
    """Its direction, in degrees from straight down."""
    return math.degrees(math.atan2(bullet.vx, -bullet.vy))


def frames(gun: Gun, seconds: float, aim: Shooter | None = None, state: GunState | None = None) -> list[int]:
    """Return the frames the gun fires on, over `seconds`."""
    aim = aim or shooter()
    state = state or GunState(cooldown=gun.delay)
    return [frame for frame in range(round(seconds / DT)) if step(gun, state, aim, DT)]


def test_patterns_aim_fan_and_ring() -> None:
    source, target = Entity(x=0, y=0.5), Entity(x=0.5, y=0.0)
    aimed = fire(Gun("aimed", 1, speed=1.0), shooter(source, target))[0]
    assert math.degrees(math.atan2(aimed.vy, aimed.vx)) == pytest.approx(-45)
    fan = fire(Gun("fan", 1, speed=1.0, count=3, spread=30), shooter(source, target))
    assert [round(degrees(b)) for b in fan] == [-30, 0, 30]
    ring = fire(Gun("ring", 1, speed=1.0, count=4, angle=90), shooter(source, target))
    assert sorted(round(degrees(b)) % 360 for b in ring) == [0, 90, 180, 270]
    heavy = fire(Gun("aimed", 1, speed=1.0, style="heavy"), shooter(source, target))[0]
    assert heavy.width == HEAVY_BULLET_SIZE


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


def test_a_volleys_shots_can_turn_one_by_one() -> None:
    gun = Gun("fan", 0.5, speed=0.5, volley=3, gap=0.1, volley_angles=(0, 30, 60))
    state = GunState(cooldown=0.0)
    shots = [shot for _ in range(30) for shot in step(gun, state, shooter(), DT)]
    assert [round(degrees(shot)) for shot in shots] == [0, 30, 60]
    assert state.volleys == 1
    assert not state.busy


@pytest.mark.parametrize(
    ("projectile", "kind", "speed"),
    [("rocket", "rocket", 0.25), ("missile", "homing_missile", 0.0), ("cluster", "cluster_bomb", 0.3)],
)
def test_guns_can_launch_projectiles_the_shots_way(projectile: str, kind: str, speed: float) -> None:
    gun = Gun("fan", interval=1.0, speed=0.0, count=3, spread=20, projectile=projectile)
    shots = fire(gun, shooter())
    assert [shot.kind for shot in shots if isinstance(shot, Enemy)] == [kind] * 3
    assert [math.hypot(shot.vx, shot.vy) for shot in shots] == pytest.approx([speed] * 3)
    first = shots[0]
    assert isinstance(first, Enemy)
    assert math.degrees(first.heading) == pytest.approx(-90 - 20)


def test_guns_can_spawn_enemies_as_they_are_or_on_their_way() -> None:
    plain = fire(Gun("fan", 1, speed=0.0, spawn="rocket"), shooter())[0]
    assert (plain.vx, plain.vy) == (0.0, -0.25)  # a rocket's own speed
    pair = fire(
        Gun("fan", 1, speed=0.0, spawn="dart", spawn_velocity=(0.3, -0.5), origins=((-0.1, 0), (0.1, 0))), shooter()
    )
    assert [(dart.vx, dart.vy) for dart in pair] == [(-0.3, -0.5), (0.3, -0.5)]  # mirrored on the left
    middle = fire(Gun("fan", 1, speed=0.0, spawn="dart", spawn_velocity=(0.3, -0.5)), shooter())[0]
    assert middle.vx == 0.3
    upwards = fire(Gun("fan", 1, speed=0.0, spawn="homing_missile", spawn_heading=90.0), shooter())[0]
    assert isinstance(upwards, Enemy)
    assert upwards.heading == pytest.approx(math.pi / 2)


def test_a_shell_can_be_timed_to_burst_where_the_player_is() -> None:
    gun = Gun("aimed", 1, speed=0.0, spawn="cluster_bomb", spawn_speed=0.5, spawn_fuse=True)
    shell = fire(gun, shooter(Entity(x=0.0, y=0.5), Entity(x=0.0, y=-0.5)))[0]
    assert isinstance(shell, Enemy)
    assert shell.timer_override == pytest.approx(1.0 / 0.5)
    assert (shell.vx, shell.vy) == pytest.approx((0.0, -0.5))


def test_accelerating_shots_start_slow_and_speed_up() -> None:
    shot = guns.styled_bullet(Gun("aimed", interval=1.0, speed=0.5, style="accel"), Entity(), 0.0, -0.5)
    assert math.hypot(shot.vx, shot.vy) < 0.5
    for _ in range(300):
        shot.move(DT)
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5 * guns.ACCEL_TOP)


def test_curving_shots_bend() -> None:
    shot = guns.styled_bullet(Gun("fan", interval=1.0, speed=0.5, style="curve", curve=90), Entity(), 0.0, -0.5)
    for _ in range(60):
        shot.move(DT)
    assert shot.vx == pytest.approx(0.5, abs=0.01)  # a quarter turn in a second, counterclockwise
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5)


def test_snaking_and_pellet_shots() -> None:
    wave = guns.styled_bullet(Gun("fan", interval=1.0, speed=0.5, style="wave"), Entity(), 0.0, -0.5)
    pellet = guns.styled_bullet(Gun("fan", interval=1.0, speed=0.5, style="pellet"), Entity(), 0.0, -0.5)
    assert type(wave).__name__ == "WaveBullet"
    assert pellet.width < 0.03


def test_reloading_counts_again_from_the_shot_or_carries_what_it_was_late_by() -> None:
    reset = frames(Gun("fan", 0.105, speed=0.5), 1.0)
    carry = frames(Gun("fan", 0.105, speed=0.5, reload="carry"), 1.0)
    assert reset[1] - reset[0] == 7  # 0.105 s is 6.3 frames: the 7th
    assert len(carry) > len(reset)  # on average, one every 6.3 frames


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


def test_a_gun_can_fire_once_when_its_state_has_some_time_left() -> None:
    gun = Gun("aimed", 0.0, speed=0.5, at=0.8)
    state = GunState(cooldown=0.0)
    assert step(gun, state, shooter(remaining=1.0), DT) == []
    assert len(step(gun, state, shooter(remaining=0.8), DT)) == 1
    assert step(gun, state, shooter(remaining=0.5), DT) == []


def test_a_gun_waiting_for_its_volley_doesnt_reload_meanwhile() -> None:
    gun = Gun(
        "fan", 0.5, speed=0.5, wait_volley=True,
        sequence=(Gun("fan", 0.0, speed=0.5, volley=3, gap=0.1), Gun("fan", 0.0, speed=0.5, count=2)),
    )  # fmt: skip
    state = GunState(cooldown=0.0)
    assert step(gun, state, shooter(), DT) == []  # the volley starts on the next frame
    shots = [len(step(gun, state, shooter(), DT)) for _ in range(round(1.0 / DT))]
    assert [count for count in shots if count] == [1, 1, 1, 2]  # three in a row, then a pair at once
    assert shots.index(2) > round((0.2 + 0.5) / DT)  # reloading started again after the volley


def test_a_sequence_takes_turns() -> None:
    gun = Gun("fan", 0.5, speed=0.0, sequence=(Gun("fan", 0, speed=0.5, angle=-10), Gun("fan", 0, speed=0.5, angle=10)))
    state = GunState(cooldown=0.0)
    shots = [shot for _ in range(round(1.6 / DT)) for shot in step(gun, state, shooter(), DT)]
    assert [round(degrees(shot)) for shot in shots] == [-10, 10, -10, 10]


def test_a_gun_can_sweep_streams_in_a_window_each_interval() -> None:
    gun = Gun("fan", 2.0, speed=0.5, window=1.0, gap=0.1, reach=60.0)
    state = GunState(cooldown=0.0)
    angles = []
    for frame in range(1, round(4.0 / DT)):
        angles += [(frame, round(degrees(shot))) for shot in step(gun, state, shooter(clock=frame * DT), DT)]
    first = [angle for frame, angle in angles if frame < 120]
    second = [angle for frame, angle in angles if frame >= 120]
    assert first[0] < 0 < first[-1]  # left to right...
    assert second[0] > 0 > second[-1]  # ...then right to left
    assert not [frame for frame, _ in angles if 60 < frame < 120]  # a pause after each sweep


def test_distances_can_be_shares_of_the_size_cubes_or_sums() -> None:
    assert distance(0.3, 0.2, 0.4) == 0.3
    assert distance("0.5w", 0.2, 0.4) == pytest.approx(0.1)
    assert distance("-0.5h", 0.2, 0.4) == pytest.approx(-0.2)
    assert distance("3v", 0.2, 0.4) == pytest.approx(3 * config.MODEL_VOXEL)
    assert distance("0.5w-0.05", 0.2, 0.4) == pytest.approx(0.05)
    assert distance("-0.5w+0.05", 0.2, 0.4) == pytest.approx(-0.05)
    with pytest.raises(ValueError, match="3x"):
        distance("3x", 0.2, 0.4)


def test_a_gun_cant_launch_enemies_without_something_to_make_them() -> None:
    with pytest.raises(NoMakerError, match="rocket"):
        fire(Gun("fan", 1, speed=0.0, spawn="rocket"), Shooter(SOURCE, None))


def test_a_laser_fires_from_the_cannons_nearest_its_offsets() -> None:
    mounts = {
        1: Mount(1, "gun", -0.1, -0.05),
        2: Mount(2, "cannon", -0.06, -0.04, depth=-0.08),
        3: Mount(3, "cannon", 0.06, -0.04, depth=-0.08),
        4: Mount(4, "missile", 0.0, -0.02),
    }
    laser = Gun("laser", 5.0, speed=0.0, offsets=(-0.1, 0.1))
    piece = Entity(x=0.2, y=0.5, width=0.4, height=0.2)
    beams = guns.laser_beams(laser, Shooter(piece, None, mounts=mounts), warning=False)
    assert [(beam.x - piece.x, beam.y + beam.height / 2 - piece.y, beam.depth) for beam in beams] == [
        pytest.approx((-0.06, -0.04, -0.08)),
        pytest.approx((0.06, -0.04, -0.08)),
    ]
    one_cannon = {number: mounts[number] for number in (1, 3, 4)}  # each weapon fires one beam
    assert len(guns.laser_beams(laser, Shooter(piece, None, mounts=one_cannon), warning=True)) == 1
    named = guns.laser_beams(replace(laser, weapons=(4,)), Shooter(piece, None, mounts=mounts), warning=False)
    assert [beam.x - piece.x for beam in named] == [pytest.approx(0.0)]
    under = guns.laser_beams(laser, Shooter(piece, None), warning=False)  # no weapons: under its middle
    assert [(beam.x - piece.x, beam.y + beam.height / 2, beam.depth) for beam in under] == [
        pytest.approx((-0.1, 0.4, 0.0)),
        pytest.approx((0.1, 0.4, 0.0)),
    ]
