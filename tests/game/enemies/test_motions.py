import math

import pytest

from pewpy import config
from pewpy.game.enemies.enemy import Enemy, create
from pewpy.game.enemies.motions import MOTIONS
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.enemies.spec import EnemySpec, Motion, Part
from pewpy.game.entities import Entity

DT = 1 / 60
TARGET = Entity(x=0.3, y=-0.75)
SCROLL = 0.2


def enemy(**fields) -> Enemy:
    made = create(EnemySpec(kind="test", width=0.1, height=0.1))
    for name, value in fields.items():
        setattr(made, name, value)
    return made


def move(moving: Enemy, motion: Motion, seconds: float = DT, target: Entity = TARGET) -> None:
    """Run the motion and move, for `seconds`."""
    for _ in range(max(1, round(seconds / DT))):
        moving.age += DT
        MOTIONS[motion.type](moving, motion, DT, target, SCROLL)
        moving.move(DT)


def test_scrolling_with_the_ground_maybe_driving_too():
    truck = enemy(vx=0.1)
    move(truck, Motion("scroll", plus=-0.15))
    assert (truck.vx, truck.vy) == (0.1, pytest.approx(-0.35))
    mine = enemy(vx=0.1)
    move(mine, Motion("scroll", stop_x=True))
    assert (mine.vx, mine.vy) == (0.0, -SCROLL)


def test_patrolling_starts_towards_the_middle():
    left, right = enemy(x=-0.5), enemy(x=0.5)
    move(left, Motion("patrol", speed=0.1))
    move(right, Motion("patrol", speed=0.1))
    assert (left.vx, right.vx) == (0.1, -0.1)
    going = enemy(x=0.5, vx=0.2)
    move(going, Motion("patrol", speed=0.1))
    assert going.vx == 0.2  # already moving sideways: left alone


def test_bouncing_off_the_edges():
    edge = HALF_WIDTH - 0.05
    out = enemy(x=edge + 0.01, vx=0.3)
    move(out, Motion("bounce"))
    assert out.vx == -0.3
    back = enemy(x=edge + 0.01, vx=-0.3)
    move(back, Motion("bounce"))
    assert back.vx == -0.3  # already coming back


def test_a_boss_bounces_with_its_parts_and_stays_inside():
    arm = EnemySpec(kind="arm", width=0.2)
    boss = create(EnemySpec(kind="boss", width=0.4, parts=(Part("arm", arm, 0.5, 0.0),)), x=HALF_WIDTH, y=0.5)
    boss.vx = 0.3
    MOTIONS["bounce"](boss, Motion("bounce", clamp=True), DT, TARGET, SCROLL)
    assert boss.vx == -0.3
    assert boss.x == pytest.approx(HALF_WIDTH - 0.6)


def test_weaving_around_its_column():
    weaver = enemy(x=0.2)
    xs = []
    for _ in range(120):
        move(weaver, Motion("weave", amplitude=0.25, widen=True, period=2.0))
        xs.append(weaver.x)
    reach = 0.25 * config.WIDTH_SCALE
    assert max(xs) == pytest.approx(0.2 + reach, abs=0.01)
    assert min(xs) == pytest.approx(0.2 - reach, abs=0.01)
    narrow = enemy(x=0.0)
    move(narrow, Motion("weave", amplitude=0.1, period=2.0), 0.5)
    assert narrow.x == pytest.approx(0.1, abs=0.001)


def test_swooping_down_then_up():
    swooper = enemy()
    move(swooper, Motion("swoop", amplitude=-0.5, rate=1.2))
    assert swooper.vy < 0
    move(swooper, Motion("swoop", amplitude=-0.5, rate=1.2), 2.0)
    assert swooper.vy > 0


def test_circling_while_coming_down():
    mite = enemy(y=0.5)
    move(mite, Motion("circle", radius=0.12, turn=3.0, descent=0.2), 2 * math.pi / 3.0)
    assert mite.x == pytest.approx(0.0, abs=0.01)  # a full turn
    assert mite.y == pytest.approx(0.5 - 0.2 * 2 * math.pi / 3.0, abs=0.01)


def test_steering_towards_the_player_or_down():
    missile = enemy(y=0.5, heading=math.pi / 2)  # launched upwards
    move(missile, Motion("steer", rate=math.radians(100), speed=0.45), 3.0, Entity(x=0.3, y=-0.75))
    assert missile.vy < 0
    assert math.hypot(missile.vx, missile.vy) == pytest.approx(0.45)
    swarmer = enemy(x=0.0, heading=0.0)
    move(swarmer, Motion("steer", goal="down", rate=0.9, widen=True, inside=True, speed=0.6), 5.0)
    assert swarmer.heading == pytest.approx(-math.pi / 2)


def test_a_steering_enemy_can_wait_to_be_inside_the_screen():
    outside = enemy(x=-HALF_WIDTH - 0.2, heading=0.0)
    MOTIONS["steer"](outside, Motion("steer", goal="down", rate=1.0, inside=True, speed=0.6), DT, TARGET, SCROLL)
    assert outside.heading == 0.0
    assert outside.vx == pytest.approx(0.6)


def test_speeding_up_to_a_top_speed():
    rocket = enemy(vy=-0.25)
    move(rocket, Motion("accelerate", rate=1.0, top=1.1), 0.1)
    assert -1.1 < rocket.vy < -0.25
    move(rocket, Motion("accelerate", rate=1.0, top=1.1), 2.0)
    assert rocket.vy == pytest.approx(-1.1)


def test_tracking_the_players_column():
    tracker = enemy(x=0.0)
    move(tracker, Motion("track_x", speed=0.2))
    assert tracker.vx == 0.2
    lined_up = enemy(x=0.29)
    move(lined_up, Motion("track_x", speed=0.2))
    assert lined_up.vx == 0.0


def test_zigzagging_first_towards_the_player():
    hornet = enemy(x=0.0)
    MOTIONS["zigzag"](hornet, Motion("zigzag", speed=0.35, every=0.6), DT, TARGET, SCROLL)
    assert hornet.vx == -0.35  # it turned at once: away from the player, at x 0.3
    for _ in range(round(0.6 / DT) + 1):
        MOTIONS["zigzag"](hornet, Motion("zigzag", speed=0.35, every=0.6), DT, TARGET, SCROLL)
    assert hornet.vx == 0.35
    leftwards = enemy(x=0.5)
    MOTIONS["zigzag"](leftwards, Motion("zigzag", speed=0.35, every=0.6), DT, TARGET, SCROLL)
    assert leftwards.vx == 0.35


def test_drifting_erratically():
    scrapper = enemy(x=0.1)
    move(scrapper, Motion("erratic", every=0.5, speed=0.25, a=2.4, b=7.0))
    first = scrapper.vx
    assert first == pytest.approx(0.25 * math.sin(2.4 + 0.1 * 7.0))
    move(scrapper, Motion("erratic", every=0.5, speed=0.25, a=2.4, b=7.0), 0.4)
    assert scrapper.vx == first  # holds its course half a second
