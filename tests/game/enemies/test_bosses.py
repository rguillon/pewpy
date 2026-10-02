import pytest

from pewpy.game.enemies.enemy import HALF_WIDTH, Enemy, create
from pewpy.game.enemies.kinds import BOSSES
from pewpy.game.enemies.roster import make_enemy
from pewpy.game.enemies.spec import parse_enemy
from pewpy.game.entities import Bullet, Entity
from pewpy.game.weapons.bullets import BossBeam
from pewpy.game.weapons.guns import LASER_WARNING

DT = 1 / 60
BELOW = Entity(x=0.0, y=-0.8)  # a target straight down the screen
PHASE_PAUSE = BOSSES["harvester"].states[1].warmup  # every phase starts with a pause


def make_boss(name: str, x: float, top: float = 1.1) -> Enemy:
    return make_enemy(name, x, 0.0, "left", None, top)


def arrive(boss: Enemy) -> list[Entity]:
    """Update the boss until it has come down and started its first phase; everything it created."""
    created = []
    for _ in range(2000):
        created += boss.update(DT, BELOW, 0.2)
        if boss.state.name != "enter":
            return created
    pytest.fail("the boss never arrived")


def fight(boss: Enemy, seconds: float) -> list[Entity]:
    created = []
    for _ in range(round(seconds / DT)):
        created += boss.update(DT, BELOW, 0.2)
    return created


def destroy(*parts: Enemy) -> None:
    for part in parts:
        part.hit(part.health)


def test_a_boss_starts_above_the_screen_and_comes_down_to_hold():
    boss = make_boss("harvester", 0.0, top=1.6)
    assert all(part.y - part.height / 2 > 1.6 for part in boss.parts)
    arrive(boss)
    assert boss.y == pytest.approx(boss.spec.states[0].exits[0].below_y, abs=0.01)  # where it holds
    assert boss.vy == 0


def test_parts_join_the_world_and_follow_the_core():
    boss = make_boss("harvester", 0.0)
    created = boss.update(DT, BELOW, 0.2)
    assert [entity for entity in created if isinstance(entity, Enemy)] == boss.parts
    fight(boss, 3.0)
    for part in boss.parts:
        assert part.x == pytest.approx(boss.x + part.offset_x)
        assert part.y == pytest.approx(boss.y + part.offset_y)


def test_a_living_part_covers_the_columns_under_it():
    boss = make_boss("reaper", 0.0)
    boss.update(DT, BELOW, 0.2)
    cutter = next(part for part in boss.parts if part.part_name == "cutter")
    assert boss.covered(cutter.x)
    assert not boss.covered(boss.x + boss.width / 2 - 0.01)  # the core's edge, no part over it
    cutter.alive = False
    assert not boss.covered(cutter.x)


def test_no_shots_while_coming_down_or_during_a_phase_pause():
    boss = make_boss("warden", 0.0)
    assert not [entity for entity in arrive(boss) if not isinstance(entity, Enemy)]
    assert fight(boss, PHASE_PAUSE - 0.1) == []
    assert fight(boss, 2.0)


def test_the_boss_sways_but_stays_on_screen():
    boss = make_boss("colossus", 0.0)
    arrive(boss)
    xs = []
    for _ in range(round(20 / DT)):
        boss.update(DT, BELOW, 0.2)
        xs.append(boss.x)
    limit = HALF_WIDTH - boss.spec.half_span
    assert max(xs) == pytest.approx(limit, abs=0.01)
    assert min(xs) == pytest.approx(-limit, abs=0.01)


def test_an_armored_core_ignores_shots_until_its_parts_are_destroyed():
    boss = make_boss("harvester", 0.0)
    arrive(boss)
    assert boss.appearance() != "armored"  # flashing: the phase starts
    fight(boss, PHASE_PAUSE)
    assert boss.appearance() == "armored"
    boss.hit(10)
    assert boss.health == BOSSES["harvester"].health
    destroy(boss.parts[0])
    fight(boss, DT)
    assert boss.state.name == "phase 1"  # one cannon left
    destroy(boss.parts[1])
    fight(boss, DT)
    assert boss.state.name == "phase 2"
    boss.hit(10)
    assert boss.health == BOSSES["harvester"].health - 10


def test_a_new_phase_changes_the_guns():
    boss = make_boss("harvester", 0.0)
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
    boss = make_boss("warden", 0.0)
    arrive(boss)
    fight(boss, PHASE_PAUSE)
    boss.hit(boss.spec.health * 0.4)
    fight(boss, DT)
    assert boss.state.name == "phase 1"
    boss.hit(boss.spec.health * 0.1)
    fight(boss, DT)
    assert boss.state.name == "phase 2"
    assert boss.warmup > 0  # a short break, flashing, before the new pattern


def test_destroyed_parts_stop_firing():
    boss = make_boss("colossus", 0.0)
    arrive(boss)
    left_outer = boss.parts[0]
    destroy(left_outer)
    shots = fight(boss, 6.0)
    assert shots
    assert not [shot for shot in shots if shot.x == pytest.approx(left_outer.x)]


def test_health_bar_counts_the_core_and_its_parts():
    boss = make_boss("harvester", 0.0)
    assert boss.health_fraction == 1.0
    destroy(boss.parts[0])
    assert boss.health_fraction == pytest.approx(1 - 40 / 180)


def test_volleys_fire_several_times_in_a_row():
    boss = make_boss("harvester", 0.0)
    arrive(boss)
    shots = fight(boss, PHASE_PAUSE + 0.5)  # the left cannon's first volley of 3, the others wait
    assert len(shots) == 3


def laser_boss(**gun) -> Enemy:
    sentinel = BOSSES["sentinel"]
    laser = {"pattern": "laser", "reload": "carry", "off_screen": "fire", **gun}
    phase = {"name": "phase 1", "motions": [{"type": "bounce", "clamp": True}], "guns": [laser], "warmup": PHASE_PAUSE}
    spec = parse_enemy("laser", {"size": [sentinel.width, sentinel.height], "states": [phase]}, "test")
    boss = create(spec, 0.0, 0.55)
    arrive(boss)
    fight(boss, PHASE_PAUSE - 0.05)  # the next update fires
    return boss


def test_a_laser_shows_a_thin_harmless_beam_a_second_before_it_fires():
    boss = laser_boss(interval=5.0, speed=0.0, width=0.07, duration=1.0, offsets=(-0.05, 0.05))
    warnings = [shot for shot in fight(boss, 0.1) if isinstance(shot, Bullet)]
    assert len(warnings) == 2
    assert all(shot.harmless and shot.style == "warning" and shot.width < 0.07 for shot in warnings)
    created = fight(boss, LASER_WARNING - 0.2)
    assert not created
    beams = [shot for shot in fight(boss, 0.2) if isinstance(shot, Bullet)]
    assert len(beams) == 2
    assert all(not beam.harmless and beam.pierces and beam.width == 0.07 for beam in beams)
    for beam in beams:
        beam.move(0.0)  # the world moves shots after the enemies
    assert {round(beam.x - boss.x, 3) for beam in beams} == {-0.05, 0.05}


def test_a_beam_follows_its_gun_and_goes_with_it():
    boss = laser_boss(interval=5.0, speed=0.0)
    beam = next(shot for shot in fight(boss, 0.1) if isinstance(shot, BossBeam))
    boss.x += 0.2
    beam.move(DT)
    assert beam.x == pytest.approx(boss.x)
    assert beam.y + beam.height / 2 == pytest.approx(boss.y - boss.height / 2)
    boss.alive = False
    beam.move(DT)
    assert not beam.alive


def test_a_boss_lights_up_when_hit_and_its_parts_too():
    boss = make_boss("rockbreaker", 0.0, 1.0)
    boss.warmup = 0.0
    boss.flash_time = 0.1
    assert boss.appearance() == "hit"
    assert boss.drawing == BOSSES["rockbreaker"].drawing
    part = boss.parts[0]
    assert part.appearance() == "normal"
    part.flash_time = 0.1
    assert part.appearance() == "hit"
