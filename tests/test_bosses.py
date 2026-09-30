import math

import pytest

from pewpy import bosses, models
from pewpy.boss_catalog import BOSSES
from pewpy.bosses import Boss, BossPart, Gun, make_boss, pattern_bullets
from pewpy.enemies import HALF_WIDTH
from pewpy.entities import Bullet, Entity
from pewpy.level import Level, Wave, load_levels, parse_level
from pewpy.world import Controls, World

DT = 1 / 60
BOSS_LEVEL = Level(name="boss", scroll_speed=0.2, waves=(Wave(time=0.0, enemy="harvester"),))
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


@pytest.mark.parametrize("kind", BOSSES)
def test_every_boss_fits_the_screen_and_its_parts_and_guns_exist(kind):
    spec = BOSSES[kind]
    assert spec.half_span < HALF_WIDTH
    names = {part.name for part in spec.parts}
    for phase in spec.phases:
        assert {source for source, _ in phase.guns} <= names | {bosses.CORE}
        assert set(phase.until_destroyed) <= names
    for drawing in {spec.drawing} | {part.drawing for part in spec.parts}:
        models.load_drawing(drawing)


@pytest.mark.parametrize("kind", BOSSES)
def test_every_part_can_be_shot_from_below(kind):
    """Shots fly up: some of each part's width must not be behind a piece that reaches lower (core included)."""
    spec = BOSSES[kind]
    pieces = [(0.0, -spec.height / 2, spec.width)] + [(p.x, p.y - p.height / 2, p.width) for p in spec.parts]
    for part in spec.parts:
        bottom, left, right = part.y - part.height / 2, part.x - part.width / 2, part.x + part.width / 2
        shots = [left + (right - left) * step / 100 for step in range(101)]
        open_shots = [
            x
            for x in shots
            if not any(low < bottom and abs(x - middle) < (width + 0.02) / 2 for middle, low, width in pieces)
        ]
        assert len(open_shots) * (right - left) / 100 >= 0.04, part.name


@pytest.mark.parametrize("kind", BOSSES)
def test_every_hitbox_has_the_shape_of_its_drawing(kind):
    """The model is drawn at the hitbox's size with square voxels: the drawing must have the same shape."""
    spec = BOSSES[kind]
    for drawing, width, height in [(spec.drawing, spec.width, spec.height)] + [
        (part.drawing, part.width, part.height) for part in spec.parts
    ]:
        rows, _ = models.load_drawing(drawing)
        assert width / height == pytest.approx(len(rows[0]) / len(rows), rel=0.12), drawing


def test_every_level_ends_with_its_own_boss():
    levels = load_levels()
    last_waves = [max(level.waves, key=lambda wave: wave.time) for level in levels]
    assert all(wave.enemy in BOSSES for wave in last_waves)
    assert sorted(wave.enemy for wave in last_waves) == sorted(BOSSES)  # each boss once
    for level in levels:
        assert sum(wave.enemy in BOSSES for wave in level.waves) == 1


@pytest.mark.parametrize("kind", BOSSES)
def test_every_phase_but_the_last_can_end(kind):
    phases = BOSSES[kind].phases
    assert all(phase.until_destroyed or phase.until_below > 0 for phase in phases[:-1])
    assert len(phases) >= 2  # several shooting patterns


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


def boss_world() -> World:
    return World(BOSS_LEVEL, seed=0)


def run(world: World, seconds: float) -> None:
    for _ in range(round(seconds / DT)):
        world.update(DT, Controls())


def test_a_boss_and_its_parts_stay_in_the_world_and_hold_the_level():
    world = boss_world()
    run(world, 0.1)
    assert world.boss is not None
    assert len(world.enemies) == 1 + len(BOSSES["harvester"].parts)
    run(world, 30)
    assert not world.completed
    assert world.boss is not None


def test_destroying_the_boss_takes_its_parts_down_and_completes_the_level():
    world = boss_world()
    run(world, 0.1)
    boss = world.boss
    assert boss is not None
    boss.parts[1].alive = False
    boss.phase_index = 1
    score = world.score
    world._damage(boss, boss.health)
    assert not boss.parts[0].alive
    assert world.score == score + boss.points  # the parts give no points when wrecked
    explosions = [event for event in world.events if event.kind == "explosion"]
    assert len(explosions) == len(bosses.EXPLOSIONS) + 1
    run(world, DT)
    assert world.completed


def test_ramming_a_boss_hurts_the_player_but_not_the_boss():
    world = boss_world()
    run(world, 0.1)
    boss = world.boss
    assert boss is not None
    boss.x, boss.y = world.player.x, world.player.y
    health = world.player.health
    world.update(DT, Controls())
    assert world.player.health < health
    assert boss.alive


def test_levels_accept_bosses():
    level = parse_level({"name": "end", "waves": [{"time": 60, "enemy": "overmind"}]})
    assert level.spawns()[0].enemy == "overmind"
