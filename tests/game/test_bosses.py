import math

import pytest

from pewpy.game import bosses
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.bosses import Boss, BossPart, Gun, make_boss, pattern_bullets
from pewpy.game.enemies import HALF_WIDTH
from pewpy.game.entities import Bullet, Entity

DT = 1 / 60
BELOW = Entity(x=0.0, y=-0.8)  # a target straight down the screen


def arrive(boss: Boss) -> list[Entity]:
    """Update the boss until it has come down and started its first phase; everything it created."""
    created = []
    for _ in range(2000):
        created += boss.update(DT, BELOW, 0.2)
        if boss.arrived:
            return created
    pytest.fail("the boss never arrived")


def fight(boss: Boss, seconds: float) -> list[Entity]:
    created = []
    for _ in range(round(seconds / DT)):
        created += boss.update(DT, BELOW, 0.2)
    return created


def destroy(*parts: BossPart) -> None:
    for part in parts:
        part.hit(part.health)


def test_a_boss_starts_above_the_screen_and_comes_down_to_hold():
    boss = make_boss(BOSSES["harvester"], 0.0, top=1.6)
    assert all(part.y - part.height / 2 > 1.6 for part in boss.parts)
    arrive(boss)
    assert boss.y == pytest.approx(bosses.HOLD_Y, abs=0.01)
    assert boss.vy == 0


def test_parts_join_the_world_and_follow_the_core():
    boss = make_boss(BOSSES["harvester"], 0.0)
    created = boss.update(DT, BELOW, 0.2)
    assert [entity for entity in created if isinstance(entity, BossPart)] == boss.parts
    fight(boss, 3.0)
    for part in boss.parts:
        assert part.x == pytest.approx(boss.x + part.offset_x)
        assert part.y == pytest.approx(boss.y + part.offset_y)


def test_no_shots_while_coming_down_or_during_a_phase_pause():
    boss = make_boss(BOSSES["warden"], 0.0)
    assert not [entity for entity in arrive(boss) if not isinstance(entity, BossPart)]
    assert fight(boss, bosses.PHASE_PAUSE - 0.1) == []
    assert fight(boss, 2.0)


def test_the_boss_sways_but_stays_on_screen():
    boss = make_boss(BOSSES["colossus"], 0.0)
    arrive(boss)
    xs = []
    for _ in range(round(20 / DT)):
        boss.update(DT, BELOW, 0.2)
        xs.append(boss.x)
    limit = HALF_WIDTH - boss.spec.half_span
    assert max(xs) == pytest.approx(limit, abs=0.01)
    assert min(xs) == pytest.approx(-limit, abs=0.01)


def test_an_armored_core_ignores_shots_until_its_parts_are_destroyed():
    boss = make_boss(BOSSES["harvester"], 0.0)
    arrive(boss)
    assert boss.appearance() != "armored"  # flashing: the phase starts
    fight(boss, bosses.PHASE_PAUSE)
    assert boss.appearance() == "armored"
    boss.hit(10)
    assert boss.health == BOSSES["harvester"].health
    destroy(boss.parts[0])
    fight(boss, DT)
    assert boss.phase_index == 0  # one cannon left
    destroy(boss.parts[1])
    fight(boss, DT)
    assert boss.phase_index == 1
    boss.hit(10)
    assert boss.health == BOSSES["harvester"].health - 10


def test_a_new_phase_changes_the_guns():
    boss = make_boss(BOSSES["harvester"], 0.0)
    arrive(boss)
    first = fight(boss, 4.0)
    assert {bullet.style for bullet in first if isinstance(bullet, Bullet)} == {
        "normal",
        "heavy",
    }  # cannons and the core's heavy fan
    destroy(*boss.parts)
    second = fight(boss, 4.0)
    assert {bullet.style for bullet in second if isinstance(bullet, Bullet)} == {"normal"}
    assert len(second) > len(first)  # rings of 14


def test_phases_can_end_on_the_core_health():
    boss = make_boss(BOSSES["warden"], 0.0)
    arrive(boss)
    fight(boss, bosses.PHASE_PAUSE)
    boss.hit(boss.spec.health * 0.4)
    fight(boss, DT)
    assert boss.phase_index == 0
    boss.hit(boss.spec.health * 0.1)
    fight(boss, DT)
    assert boss.phase_index == 1
    assert boss.pause > 0  # a short break, flashing, before the new pattern


def test_destroyed_parts_stop_firing():
    boss = make_boss(BOSSES["colossus"], 0.0)
    arrive(boss)
    left_outer = boss.parts[0]
    destroy(left_outer)
    shots = fight(boss, 6.0)
    assert shots
    assert not [shot for shot in shots if shot.x == pytest.approx(left_outer.x)]


def test_health_bar_counts_the_core_and_its_parts():
    boss = make_boss(BOSSES["harvester"], 0.0)
    assert boss.health_fraction == 1.0
    destroy(boss.parts[0])
    assert boss.health_fraction == pytest.approx(1 - 40 / 180)


def test_patterns_aim_fan_and_ring():
    source, target = Entity(x=0, y=0.5), Entity(x=0.5, y=0.0)
    aimed = pattern_bullets(Gun("aimed", 1, speed=1.0), source, target, 0.0, 0.0)[0]
    assert math.degrees(math.atan2(aimed.vy, aimed.vx)) == pytest.approx(-45)
    fan = pattern_bullets(Gun("fan", 1, speed=1.0, count=3, spread=30), source, target, 0.0, 0.0)
    assert [round(math.degrees(math.atan2(b.vx, -b.vy))) for b in fan] == [-30, 0, 30]
    ring = pattern_bullets(Gun("ring", 1, speed=1.0, count=4), source, target, 90.0, 0.0)
    assert sorted(round(math.degrees(math.atan2(b.vx, -b.vy))) % 360 for b in ring) == [0, 90, 180, 270]
    heavy = pattern_bullets(Gun("aimed", 1, speed=1.0, style="heavy"), source, target, 0.0, 0.0)[0]
    assert heavy.width == bosses.HEAVY_BULLET_SIZE


def test_volleys_fire_several_times_in_a_row():
    boss = make_boss(BOSSES["harvester"], 0.0)
    arrive(boss)
    shots = fight(boss, bosses.PHASE_PAUSE + 0.5)  # the left cannon's first volley of 3, the others wait
    assert len(shots) == 3
