import math

import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.enemy import boss_guns
from pewpy.game.weapons.enemy.boss_guns import Gun, pattern_bullets
from pewpy.game.weapons.enemy.shots import HEAVY_BULLET_SIZE

DT = 1 / 60
BELOW = Entity(x=0.0, y=-0.8)  # a target straight down the screen


def test_patterns_aim_fan_and_ring():
    source, target = Entity(x=0, y=0.5), Entity(x=0.5, y=0.0)
    aimed = pattern_bullets(Gun("aimed", 1, speed=1.0), source, target, 0.0, 0.0)[0]
    assert math.degrees(math.atan2(aimed.vy, aimed.vx)) == pytest.approx(-45)
    fan = pattern_bullets(Gun("fan", 1, speed=1.0, count=3, spread=30), source, target, 0.0, 0.0)
    assert [round(math.degrees(math.atan2(b.vx, -b.vy))) for b in fan] == [-30, 0, 30]
    ring = pattern_bullets(Gun("ring", 1, speed=1.0, count=4), source, target, 90.0, 0.0)
    assert sorted(round(math.degrees(math.atan2(b.vx, -b.vy))) % 360 for b in ring) == [0, 90, 180, 270]
    heavy = pattern_bullets(Gun("aimed", 1, speed=1.0, style="heavy"), source, target, 0.0, 0.0)[0]
    assert heavy.width == HEAVY_BULLET_SIZE


@pytest.mark.parametrize(
    ("projectile", "kind"),
    [("rocket", "Rocket"), ("missile", "HomingMissile"), ("cluster", "ClusterBomb")],
)
def test_guns_can_launch_projectiles(projectile, kind):
    gun = Gun("fan", interval=1.0, speed=0.0, count=3, spread=20, projectile=projectile)
    shots = boss_guns.pattern_shots(gun, Entity(x=0.0, y=0.5), BELOW, 0.0, 0.0)
    assert [type(shot).__name__ for shot in shots] == [kind] * 3


def test_accelerating_shots_start_slow_and_speed_up():
    shot = boss_guns.styled_bullet(Gun("aimed", interval=1.0, speed=0.5, style="accel"), Entity(), 0.0, -0.5)
    assert math.hypot(shot.vx, shot.vy) < 0.5
    for _ in range(300):
        shot.move(DT)
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5 * boss_guns.ACCEL_TOP)


def test_curving_shots_bend():
    shot = boss_guns.styled_bullet(Gun("fan", interval=1.0, speed=0.5, style="curve", curve=90), Entity(), 0.0, -0.5)
    for _ in range(60):
        shot.move(DT)
    assert shot.vx == pytest.approx(0.5, abs=0.01)  # a quarter turn in a second, counterclockwise
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5)


def test_snaking_and_pellet_shots():
    wave = boss_guns.styled_bullet(Gun("fan", interval=1.0, speed=0.5, style="wave"), Entity(), 0.0, -0.5)
    pellet = boss_guns.styled_bullet(Gun("fan", interval=1.0, speed=0.5, style="pellet"), Entity(), 0.0, -0.5)
    assert type(wave).__name__ == "WaveBullet"
    assert pellet.width < 0.03
