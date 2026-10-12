import math
from typing import Any

import pytest

from pewpy import config
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.exits import BelowY
from pewpy.game.enemies.kinds import BOSSES
from pewpy.game.enemies.roster import make_enemy
from pewpy.game.enemies.screen import BOTTOM, HALF_WIDTH
from pewpy.game.enemies.spec import EnemySpec, Part, parse_enemy
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import BossBeam, Bullet
from pewpy.game.weapons.guns import LASER_WARNING

DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)
SCROLL = 0.2


def described(data: dict[str, Any], x: float = 0.0, y: float = 0.5) -> Enemy:
    """Make an enemy described like in the JSON files."""
    return Enemy.from_spec(parse_enemy("test", data, "test"), x, y)


def run(enemy: Enemy, seconds: float, target: Entity = TARGET) -> list[Entity]:
    created = []
    for _ in range(max(1, round(seconds / DT))):
        created += enemy.update(DT, target, SCROLL)
    return created


def bullets(created: list[Entity]) -> list[Bullet]:
    return [entity for entity in created if isinstance(entity, Bullet)]


def states(*names: str, **first: object) -> list[dict[str, Any]]:
    return [{"name": names[0], **first}, *({"name": name} for name in names[1:])]


def test_an_enemy_starts_as_described() -> None:
    drone = Enemy.of_kind("drone", 0.1, 0.9)
    assert (drone.x, drone.y, drone.vy, drone.health, drone.points) == (0.1, 0.9, -0.3, 3.0, 100)
    assert (drone.kind, drone.kind_name, drone.drawing) == ("drone", "drone", "drone")
    assert Enemy.of_kind("dart").kind_name == "dart"  # its drawing


def test_a_timer_runs_out_then_the_state_changes() -> None:
    enemy = described({"states": states("wait", "go", timer=0.5, exits=[{"to": "go", "timer": True}])})
    run(enemy, 0.4)
    assert enemy.state.name == "wait"
    run(enemy, 0.2)
    assert enemy.state.name == "go"


def test_states_can_end_after_a_while_on_their_height_or_lined_up_with_the_player() -> None:
    clock = described({"states": states("a", "b", exits=[{"to": "b", "clock": 1.0}])})
    run(clock, 0.9)
    assert clock.state.name == "a"
    run(clock, 0.2)
    assert clock.state.name == "b"
    falling = described({"velocity": [0, -1.0], "states": states("a", "b", exits=[{"to": "b", "below_y": 0.3}])})
    run(falling, 0.3)
    assert falling.state.name == "b"
    rising = described({"velocity": [0, 1.0], "states": states("a", "b", exits=[{"to": "b", "above_y": 0.7}])})
    run(rising, 0.3)
    assert rising.state.name == "b"
    aiming = described({"states": states("a", "b", exits=[{"to": "b", "aligned": 0.05}])}, x=0.3)
    run(aiming, 0.1)
    assert aiming.state.name == "a"
    run(aiming, 0.1, Entity(x=0.32, y=-0.75))
    assert aiming.state.name == "b"


def test_states_can_follow_a_cycle_of_its_age() -> None:
    blinker = described({
        "states": [
            {"name": "on", "exits": [{"to": "off", "cycle": [1.0, 0.6, 1.0]}]},
            {"name": "off", "exits": [{"to": "on", "cycle": [1.0, 0.0, 0.6]}]},
        ]
    })
    seen = []
    for _ in range(round(2.0 / DT)):
        blinker.update(DT, TARGET, SCROLL)
        seen.append(blinker.state.name)
    assert seen.count("off") == pytest.approx(0.8 / DT, abs=2)


def test_a_state_can_be_left_differently_after_some_visits() -> None:
    looping = described(
        {
            "states": [
                {"name": "a", "timer": 0.1,
                 "exits": [{"to": "done", "timer": True, "visits": 3}, {"to": "a", "timer": True}]},
                {"name": "done"},
            ]
        }
    )  # fmt: skip
    run(looping, 0.25)
    assert looping.state.name == "a"
    assert looping.visits == 3
    run(looping, 0.15)
    assert looping.state.name == "done"


def test_a_state_can_wait_for_its_guns_to_be_idle() -> None:
    gun = {"pattern": "fan", "interval": 0.5, "speed": 0.5, "volley": 5, "gap": 0.1, "off_screen": "fire"}
    busy = described({"states": states("a", "b", guns=[gun], exits=[{"to": "b", "clock": 0.1, "idle": True}])})
    run(busy, 0.2)
    assert busy.state.name == "a"  # in the middle of its volley
    run(busy, 0.5)
    assert busy.state.name == "b"


def test_a_state_can_end_after_some_volleys_right_after_firing() -> None:
    gun = {"pattern": "fan", "interval": 0.3, "speed": 0.5, "off_screen": "fire"}
    then = [{"type": "velocity", "vy": -0.6}]
    blaster = described({"states": states("a", "b", guns=[gun], exits=[{"to": "b", "volleys": 2, "then": then}])})
    created = run(blaster, 0.7)
    assert len(bullets(created)) == 2
    assert blaster.state.name == "b"
    assert blaster.vy == -0.6


def test_actions_set_its_speed() -> None:
    left = described(
        {"states": states("a", "b", exits=[{"to": "b", "then": [{"type": "toward_middle", "speed": 0.2}]}])}, x=-0.4
    )
    run(left, DT)
    assert left.vx == 0.2
    right = described(
        {"states": states("a", "b", exits=[{"to": "b", "then": [{"type": "toward_middle", "speed": 0.2}]}])}, x=0.4
    )
    run(right, DT)
    assert right.vx == -0.2
    diver = described({"states": states("a", "b", exits=[{"to": "b", "then": [{"type": "aim", "speed": 1.2}]}])}, x=0.3)
    run(diver, DT)
    assert math.hypot(diver.vx, diver.vy) == pytest.approx(1.2)
    assert diver.vx < 0
    on_target = described(
        {"states": states("a", "b", exits=[{"to": "b", "then": [{"type": "aim", "speed": 1.2}]}])}, y=-0.75
    )
    run(on_target, DT, Entity(x=0.0, y=-0.75))
    assert (on_target.vx, on_target.vy) == (0.0, 0.0)
    dart = described(
        {"states": states("a", "b", exits=[{"to": "b", "then": [{"type": "swerve", "gain": 2.0, "limit": 0.8}]}])},
        x=-0.6,
    )
    run(dart, DT, Entity(x=0.0, y=-0.75))
    assert dart.vx == 0.8
    swayer = described({
        "velocity": [-0.1, 0],
        "states": states("a", "b", exits=[{"to": "b", "then": [{"type": "sway", "speed": 0.1}]}]),
    })
    run(swayer, DT)
    assert swayer.vx == pytest.approx(-0.1 * config.WIDTH_SCALE)  # keeps its way
    keeping = described({
        "velocity": [0.1, -0.2],
        "states": states("a", "b", exits=[{"to": "b", "then": [{"type": "velocity"}]}]),
    })
    run(keeping, DT)
    assert (keeping.vx, keeping.vy) == (0.1, -0.2)
    still = described({
        "velocity": [0.1, 0],
        "states": states("a", "b", exits=[{"to": "b", "then": [{"type": "sway", "speed": 0.1}]}]),
    })
    still.vx = 0.0
    run(still, DT)
    assert still.vx > 0  # still: goes right


def test_actions_move_it_fire_or_end_it() -> None:
    wisp = described(
        {"size": [0.1, 0.1],
         "states": states("a", "b", exits=[{"to": "b", "then": [{"type": "relocate", "step": 0.618, "dy": -0.15}]}])}
    )  # fmt: skip
    run(wisp, DT)
    span = HALF_WIDTH - 0.1
    assert wisp.x == pytest.approx(((0.0 / span + 1) / 2 + 0.618) % 1.0 * 2 * span - span)
    assert wisp.y == pytest.approx(0.5 - 0.15)
    tick = described({"start": [{"type": "to_bottom"}]})
    run(tick, DT)
    assert tick.y == pytest.approx(BOTTOM - tick.height)
    ring = {"pattern": "ring", "interval": 0, "speed": 0.4, "count": 8}
    bomb = described({
        "states": states("a", "b", exits=[{"to": "b", "then": [{"type": "die"}, {"type": "fire", "gun": ring}]}])
    })
    assert len(bullets(run(bomb, DT))) == 8
    assert not bomb.alive


def test_a_fire_action_waits_to_be_on_screen_unless_told_otherwise() -> None:
    exits = [{"to": "b", "then": [{"type": "fire", "gun": {"pattern": "fan", "interval": 0, "speed": 0.4}}]}]
    above = described({"states": states("a", "b", exits=exits)}, y=1.5)
    assert run(above, DT) == []


def test_the_frame_can_go_on_in_the_new_state_and_check_it_once_more() -> None:
    boss = described({
        "states": [
            {"name": "enter", "exits": [{"to": "one", "below_y": 0.6, "go_on": True, "recheck": True}]},
            {"name": "one", "exits": [{"to": "two", "below_y": 0.6, "go_on": True}]},
            {"name": "two", "exits": [{"to": "three", "below_y": 0.6, "go_on": True}]},
            {"name": "three"},
        ]
    })
    run(boss, DT)
    assert boss.state.name == "two"  # one change, checked again: a second one, no more
    run(boss, DT)
    assert boss.state.name == "three"


def test_a_warming_up_state_doesnt_fire_and_blinks() -> None:
    gun = {"pattern": "fan", "interval": 0.5, "speed": 0.5, "off_screen": "fire"}
    phase = described({"states": [{"name": "phase", "warmup": 0.5, "guns": [gun]}]})
    looks = set()
    created = []
    for _ in range(round(0.45 / DT)):
        created += phase.update(DT, TARGET, SCROLL)
        looks.add(phase.appearance())
    assert created == []
    assert looks == {"flash", "normal"}
    assert bullets(run(phase, 0.2))


def test_how_it_looks() -> None:
    blinking = described({"states": [{"name": "wait", "timer": 0.8, "look": "hidden", "blink": 0.1, "blink_on": 1}]})
    seen = set()
    for _ in range(40):
        blinking.update(DT, TARGET, SCROLL)
        seen.add(blinking.appearance())
    assert seen == {"hidden", "normal"}
    blinking.timer = 0.65  # shown: flashes when hit
    blinking.hit(0.1)
    assert blinking.appearance() == "flash"
    shielded = described({"states": [{"name": "a", "look": "shield", "vulnerable": False}]})
    shielded.flash_time = 0.05
    assert shielded.appearance() == "shield"
    armored = described({"hit_look": "hit", "states": [{"name": "a", "look": "armored"}]})
    assert armored.appearance() == "armored"
    armored.hit(0.1)
    assert armored.appearance() == "hit"
    plain = described({"hit_look": "hit"})
    assert plain.appearance() == "normal"


def test_a_charging_gun_makes_it_glow_and_a_holding_one_stops_it() -> None:
    gun = {
        "pattern": "beam",
        "interval": 1.0,
        "speed": 0,
        "charge": 0.5,
        "hold": True,
        "duration": 0.3,
        "staggered": True,
    }
    lancer = described(
        {"states": [{"name": "a", "motions": [{"type": "track_x", "speed": 0.2}], "guns": [gun]}]}, x=0.3
    )
    lancer.fire_cooldown = 0.05
    run(lancer, 0.1)
    assert lancer.appearance() == "flash"
    assert lancer.vx == 0.0  # held still, not tracking
    beams = bullets(run(lancer, 0.5))
    assert len(beams) == 1
    assert lancer.vx == 0.0
    run(lancer, 0.4)
    assert lancer.vx == -0.2  # free again: tracking the player
    assert lancer.fire_interval == 1.0


def test_an_enemy_without_a_staggered_gun_has_the_default_fire_interval() -> None:
    assert described({}).fire_interval == 1.0


def test_shot_down_it_can_release_enemies() -> None:
    splitter = Enemy.of_kind("splitter", 0.1, 0.4)
    released = splitter.on_destroyed()
    assert [enemy.kind for enemy in released] == ["swarmer"] * 3
    assert [round(math.degrees(enemy.heading)) for enemy in released] == [-135, -90, -45]
    assert all((enemy.x, enemy.y) == (0.1, 0.4) for enemy in released)
    assert Enemy.of_kind("drone").on_destroyed() == []


def test_a_shield_keeps_shots_out() -> None:
    shielded = described({"health": 5.0, "states": [{"name": "a", "vulnerable": False}]})
    shielded.hit(3.0)
    assert shielded.health == 5.0
    assert shielded.flash_time == 0.0
    plain = described({"health": 5.0})
    plain.hit(5.0)
    assert not plain.alive


def test_explosions_one_in_the_middle_or_as_described() -> None:
    one = described({"size": [0.1, 0.2]}, x=0.1, y=0.2)
    assert one.explosions() == [(0.1, 0.2, 0.2)]
    many = described({"size": [0.2, 0.1], "explosions": [[0.5, 0.0, 1.0], [0.0, -0.5, 0.5]]}, x=0.0, y=0.0)
    assert many.explosions() == [(0.1, 0.0, 0.2), (0.0, -0.05, 0.1)]


def boss_with_arms() -> Enemy:
    arm = EnemySpec(kind="arm", drawing="arm", width=0.1, height=0.1, health=10.0)
    gun = parse_enemy(
        "core",
        {"states": [{"name": "a",
                     "guns": [{"from": "left", "pattern": "fan", "interval": 0.2, "speed": 0.5,
                               "off_screen": "fire"}]}]},
        "test",
    ).states  # fmt: skip
    spec = EnemySpec(
        kind="core", width=0.3, height=0.2, health=20.0, boss=True, states=gun,
        parts=(Part("left", arm, -0.3, 0.0), Part("right", arm, 0.3, 0.0)),
    )  # fmt: skip
    return Enemy.from_spec(spec, 0.0, 0.5)


def test_parts_join_with_the_enemy_follow_it_and_fire_from_where_they_are() -> None:
    boss = boss_with_arms()
    left, right = boss.parts
    assert (left.part_name, left.x, right.x) == ("left", -0.3, 0.3)
    boss.vx = 0.6
    created = boss.update(DT, TARGET, SCROLL)
    assert created[:2] == [left, right]
    assert left.x == pytest.approx(boss.x - 0.3)
    shots = bullets(run(boss, 0.5))
    assert shots
    assert all(shot.x < boss.x for shot in shots)
    left.alive = False
    assert bullets(run(boss, 0.5)) == []  # it's gone: its gun is silent
    assert boss.wreckage() == [right]


def test_parts_cover_the_columns_under_them_and_count_in_its_health() -> None:
    boss = boss_with_arms()
    left, _ = boss.parts
    assert boss.covered(-0.3)
    assert not boss.covered(0.0)
    assert boss.health_fraction == 1.0
    left.health = 0.0
    left.alive = False
    assert boss.health_fraction == pytest.approx(30 / 40)
    assert not boss.covered(-0.3)


def test_an_exit_can_wait_for_parts_or_lost_health() -> None:
    boss = boss_with_arms()
    spec = parse_enemy(
        "core",
        {"states": [{"name": "a", "exits": [{"to": "b", "parts": ["left"]}, {"to": "c", "health_below": 0.5}]},
                    {"name": "b"}, {"name": "c"}]},
        "test",
    )  # fmt: skip
    boss.spec = EnemySpec(kind="core", health=20.0, states=spec.states, parts=boss.spec.parts)
    run(boss, DT)
    assert boss.state.name == "a"
    boss.parts[0].alive = False
    run(boss, DT)
    assert boss.state.name == "b"
    boss.go_to("a")
    boss.parts[0].alive = True
    boss.health = 9.0
    run(boss, DT)
    assert boss.state.name == "c"


def test_entering_from_a_side() -> None:
    crosser = described({"side_entry": True, "side_speed": 0.2})
    crosser.enter_from_side(-1)
    assert crosser.vx == pytest.approx(-0.2 * config.WIDTH_SCALE)
    assert crosser.heading == math.pi
    steering = described({"side_entry": True})
    steering.enter_from_side(1)
    assert steering.vx == 0.0
    assert steering.heading == 0.0


def test_its_model_turns_as_described_or_as_its_state_says() -> None:
    diver = Enemy.of_kind("diver")
    assert diver.facing == ""
    assert not diver.faces_travel
    diver.go_to("dive")
    assert diver.faces_travel
    assert Enemy.of_kind("turret").facing == "player"


def test_made_on_its_way_or_with_another_first_timer() -> None:
    shell = Enemy.of_kind("cluster_bomb", 0.0, 0.5, heading=1.0, timer=0.1)
    assert shell.heading == 1.0
    run(shell, 0.15)
    assert not shell.alive  # burst early


# Bosses: the tests' own (see conftest.py), written with phases and parts.
BELOW = Entity(x=0.0, y=-0.8)  # a target straight down the screen


PHASE_PAUSE = BOSSES["sentinel"].states[1].warmup  # every phase starts with a pause


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


@pytest.mark.usefixtures("test_bosses")
def test_a_boss_starts_above_the_screen_and_comes_down_to_hold() -> None:
    boss = make_boss("test_harvester", 0.0, top=1.6)
    assert all(part.y - part.height / 2 > 1.6 for part in boss.parts)
    arrive(boss)
    (hold,) = boss.spec.states[0].exits[0].conditions
    assert isinstance(hold, BelowY)
    assert boss.y == pytest.approx(hold.y, abs=0.01)  # where it holds
    assert boss.vy == 0


@pytest.mark.usefixtures("test_bosses")
def test_parts_join_the_world_and_follow_the_core() -> None:
    boss = make_boss("test_harvester", 0.0)
    created = boss.update(DT, BELOW, 0.2)
    assert [entity for entity in created if isinstance(entity, Enemy)] == boss.parts
    fight(boss, 3.0)
    for part in boss.parts:
        assert part.mount is not None
        assert part.x == pytest.approx(boss.x + part.mount.x)
        assert part.y == pytest.approx(boss.y + part.mount.y)


@pytest.mark.usefixtures("test_bosses")
def test_a_living_part_covers_the_columns_under_it() -> None:
    boss = make_boss("test_reaper", 0.0)
    boss.update(DT, BELOW, 0.2)
    cutter = next(part for part in boss.parts if part.part_name == "cutter")
    assert boss.covered(cutter.x)
    assert not boss.covered(boss.x + boss.width / 2 - 0.01)  # the core's edge, no part over it
    cutter.alive = False
    assert not boss.covered(cutter.x)


@pytest.mark.usefixtures("test_bosses")
def test_a_boss_and_its_parts_cannot_be_hurt_until_they_come_to_their_place() -> None:
    boss = make_boss("test_harvester", 0.0)
    boss.update(DT, BELOW, 0.2)
    destroy(boss, *boss.parts)
    assert boss.alive
    assert all(part.alive for part in boss.parts)
    assert boss.health_fraction == 1.0
    arrive(boss)
    destroy(*boss.parts)
    assert not any(part.alive for part in boss.parts)


@pytest.mark.usefixtures("test_bosses")
def test_no_shots_while_coming_down_or_during_a_phase_pause() -> None:
    boss = make_boss("warden", 0.0)
    assert not [entity for entity in arrive(boss) if not isinstance(entity, Enemy)]
    assert fight(boss, PHASE_PAUSE - 0.1) == []
    assert fight(boss, 2.0)


@pytest.mark.usefixtures("test_bosses")
def test_the_boss_sways_but_stays_on_screen() -> None:
    boss = make_boss("test_colossus", 0.0)
    arrive(boss)
    xs = []
    for _ in range(round(20 / DT)):
        boss.update(DT, BELOW, 0.2)
        xs.append(boss.x)
    limit = HALF_WIDTH - boss.spec.half_span
    assert max(xs) == pytest.approx(limit, abs=0.01)
    assert min(xs) == pytest.approx(-limit, abs=0.01)


@pytest.mark.usefixtures("test_bosses")
def test_an_armored_core_ignores_shots_until_its_parts_are_destroyed() -> None:
    boss = make_boss("test_harvester", 0.0)
    arrive(boss)
    assert boss.appearance() != "armored"  # flashing: the phase starts
    fight(boss, PHASE_PAUSE)
    assert boss.appearance() == "armored"
    boss.hit(10)
    assert boss.health == BOSSES["test_harvester"].health
    destroy(boss.parts[0])
    fight(boss, DT)
    assert boss.state.name == "phase 1"  # one cannon left
    destroy(boss.parts[1])
    fight(boss, DT)
    assert boss.state.name == "phase 2"
    boss.hit(10)
    assert boss.health == BOSSES["test_harvester"].health - 10


@pytest.mark.usefixtures("test_bosses")
def test_a_new_phase_changes_the_guns() -> None:
    boss = make_boss("test_harvester", 0.0)
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


@pytest.mark.usefixtures("test_bosses")
def test_phases_can_end_on_the_core_health() -> None:
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


@pytest.mark.usefixtures("test_bosses")
def test_destroyed_parts_stop_firing() -> None:
    boss = make_boss("test_colossus", 0.0)
    arrive(boss)
    left_outer = boss.parts[0]
    destroy(left_outer)
    shots = fight(boss, 6.0)
    assert shots
    assert not [shot for shot in shots if shot.x == pytest.approx(left_outer.x)]


@pytest.mark.usefixtures("test_bosses")
def test_health_bar_counts_the_core_and_its_parts() -> None:
    boss = make_boss("test_harvester", 0.0)
    assert boss.health_fraction == 1.0
    arrive(boss)
    destroy(boss.parts[0])
    assert boss.health_fraction == pytest.approx(1 - 40 / 180)


@pytest.mark.usefixtures("test_bosses")
def test_volleys_fire_several_times_in_a_row() -> None:
    boss = make_boss("test_harvester", 0.0)
    arrive(boss)
    shots = fight(boss, PHASE_PAUSE + 0.5)  # the left cannon's first volley of 3, the others wait
    assert len(shots) == 3


def laser_boss(**gun: object) -> Enemy:
    sentinel = BOSSES["sentinel"]
    laser = {"pattern": "laser", "reload": "carry", "off_screen": "fire", **gun}
    phase = {"name": "phase 1", "motions": [{"type": "bounce", "clamp": True}], "guns": [laser], "warmup": PHASE_PAUSE}
    spec = parse_enemy("laser", {"size": [sentinel.width, sentinel.height], "states": [phase]}, "test")
    boss = Enemy.from_spec(spec, 0.0, 0.55)
    arrive(boss)
    fight(boss, PHASE_PAUSE - 0.05)  # the next update fires
    return boss


@pytest.mark.usefixtures("test_bosses")
def test_a_laser_shows_a_thin_harmless_beam_a_second_before_it_fires() -> None:
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


@pytest.mark.usefixtures("test_bosses")
def test_a_beam_follows_its_gun_and_goes_with_it() -> None:
    boss = laser_boss(interval=5.0, speed=0.0)
    beam = next(shot for shot in fight(boss, 0.1) if isinstance(shot, BossBeam))
    boss.x += 0.2
    beam.move(DT)
    assert beam.x == pytest.approx(boss.x)
    assert beam.y + beam.height / 2 == pytest.approx(boss.y - boss.height / 2)
    boss.alive = False
    beam.move(DT)
    assert not beam.alive


@pytest.mark.usefixtures("test_bosses")
def test_a_boss_lights_up_when_hit_and_its_parts_too() -> None:
    boss = make_boss("rockbreaker", 0.0, 1.0)
    boss.warmup = 0.0
    boss.flash_time = 0.1
    assert boss.appearance() == "hit"
    assert boss.drawing == BOSSES["rockbreaker"].drawing
    part = boss.parts[0]
    assert part.appearance() == "normal"
    part.flash_time = 0.1
    assert part.appearance() == "hit"
