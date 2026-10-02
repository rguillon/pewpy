import math
from typing import Any

import pytest

from pewpy import config
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.screen import BOTTOM, HALF_WIDTH
from pewpy.game.enemies.spec import EnemySpec, Part, parse_enemy
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet

DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)
SCROLL = 0.2


def described(data: dict[str, Any], x: float = 0.0, y: float = 0.5) -> Enemy:
    """An enemy described like in the JSON files."""
    return Enemy.from_spec(parse_enemy("test", data, "test"), x, y)


def run(enemy: Enemy, seconds: float, target: Entity = TARGET) -> list[Entity]:
    created = []
    for _ in range(max(1, round(seconds / DT))):
        created += enemy.update(DT, target, SCROLL)
    return created


def bullets(created: list[Entity]) -> list[Bullet]:
    return [entity for entity in created if isinstance(entity, Bullet)]


def states(*names: str, **first: Any) -> list[dict[str, Any]]:
    return [{"name": names[0], **first}, *({"name": name} for name in names[1:])]


def test_an_enemy_starts_as_described():
    drone = Enemy.of_kind("drone", 0.1, 0.9)
    assert (drone.x, drone.y, drone.vy, drone.health, drone.points) == (0.1, 0.9, -0.3, 3.0, 100)
    assert (drone.kind, drone.kind_name, drone.drawing) == ("drone", "drone", "drone")
    assert Enemy.of_kind("dart").kind_name == "dart"  # its drawing


def test_a_timer_runs_out_then_the_state_changes():
    enemy = described({"states": states("wait", "go", timer=0.5, exits=[{"to": "go", "timer": True}])})
    run(enemy, 0.4)
    assert enemy.state.name == "wait"
    run(enemy, 0.2)
    assert enemy.state.name == "go"


def test_states_can_end_after_a_while_on_their_height_or_lined_up_with_the_player():
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


def test_states_can_follow_a_cycle_of_its_age():
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


def test_a_state_can_be_left_differently_after_some_visits():
    looping = described(
        {
            "states": [
                {"name": "a", "timer": 0.1, "exits": [{"to": "done", "timer": True, "visits": 3}, {"to": "a", "timer": True}]},
                {"name": "done"},
            ]
        }
    )  # fmt: skip
    run(looping, 0.25)
    assert looping.state.name == "a" and looping.visits == 3
    run(looping, 0.15)
    assert looping.state.name == "done"


def test_a_state_can_wait_for_its_guns_to_be_idle():
    gun = {"pattern": "fan", "interval": 0.5, "speed": 0.5, "volley": 5, "gap": 0.1, "off_screen": "fire"}
    busy = described({"states": states("a", "b", guns=[gun], exits=[{"to": "b", "clock": 0.1, "idle": True}])})
    run(busy, 0.2)
    assert busy.state.name == "a"  # in the middle of its volley
    run(busy, 0.5)
    assert busy.state.name == "b"


def test_a_state_can_end_after_some_volleys_right_after_firing():
    gun = {"pattern": "fan", "interval": 0.3, "speed": 0.5, "off_screen": "fire"}
    then = [{"type": "velocity", "vy": -0.6}]
    blaster = described({"states": states("a", "b", guns=[gun], exits=[{"to": "b", "volleys": 2, "then": then}])})
    created = run(blaster, 0.7)
    assert len(bullets(created)) == 2
    assert blaster.state.name == "b" and blaster.vy == -0.6


def test_actions_set_its_speed():
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
    assert math.hypot(diver.vx, diver.vy) == pytest.approx(1.2) and diver.vx < 0
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


def test_actions_move_it_fire_or_end_it():
    wisp = described(
        {"size": [0.1, 0.1], "states": states("a", "b", exits=[{"to": "b", "then": [{"type": "relocate", "step": 0.618, "dy": -0.15}]}])}
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


def test_a_fire_action_waits_to_be_on_screen_unless_told_otherwise():
    exits = [{"to": "b", "then": [{"type": "fire", "gun": {"pattern": "fan", "interval": 0, "speed": 0.4}}]}]
    above = described({"states": states("a", "b", exits=exits)}, y=1.5)
    assert run(above, DT) == []


def test_the_frame_can_go_on_in_the_new_state_and_check_it_once_more():
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


def test_a_warming_up_state_doesnt_fire_and_blinks():
    gun = {"pattern": "fan", "interval": 0.5, "speed": 0.5, "off_screen": "fire"}
    phase = described({"states": [{"name": "phase", "warmup": 0.5, "guns": [gun]}]})
    looks = set()
    created = []
    for _ in range(round(0.45 / DT)):
        created += phase.update(DT, TARGET, SCROLL)
        looks.add(phase.appearance())
    assert created == [] and looks == {"flash", "normal"}
    assert bullets(run(phase, 0.2))


def test_how_it_looks():
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


def test_a_charging_gun_makes_it_glow_and_a_holding_one_stops_it():
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
    assert len(beams) == 1 and lancer.vx == 0.0
    run(lancer, 0.4)
    assert lancer.vx == -0.2  # free again: tracking the player
    assert lancer.fire_interval == 1.0


def test_an_enemy_without_a_staggered_gun_has_the_default_fire_interval():
    assert described({}).fire_interval == 1.0


def test_shot_down_it_can_release_enemies():
    splitter = Enemy.of_kind("splitter", 0.1, 0.4)
    released = splitter.on_destroyed()
    assert [enemy.kind for enemy in released] == ["swarmer"] * 3
    assert [round(math.degrees(enemy.heading)) for enemy in released] == [-135, -90, -45]
    assert all((enemy.x, enemy.y) == (0.1, 0.4) for enemy in released)
    assert Enemy.of_kind("drone").on_destroyed() == []


def test_a_shield_keeps_shots_out():
    shielded = described({"health": 5.0, "states": [{"name": "a", "vulnerable": False}]})
    shielded.hit(3.0)
    assert shielded.health == 5.0 and shielded.flash_time == 0.0
    plain = described({"health": 5.0})
    plain.hit(5.0)
    assert not plain.alive


def test_explosions_one_in_the_middle_or_as_described():
    one = described({"size": [0.1, 0.2]}, x=0.1, y=0.2)
    assert one.explosions() == [(0.1, 0.2, 0.2)]
    many = described({"size": [0.2, 0.1], "explosions": [[0.5, 0.0, 1.0], [0.0, -0.5, 0.5]]}, x=0.0, y=0.0)
    assert many.explosions() == [(0.1, 0.0, 0.2), (0.0, -0.05, 0.1)]


def boss_with_arms() -> Enemy:
    arm = EnemySpec(kind="arm", drawing="arm", width=0.1, height=0.1, health=10.0)
    gun = parse_enemy(
        "core",
        {"states": [{"name": "a", "guns": [{"from": "left", "pattern": "fan", "interval": 0.2, "speed": 0.5, "off_screen": "fire"}]}]},
        "test",
    ).states  # fmt: skip
    spec = EnemySpec(
        kind="core", width=0.3, height=0.2, health=20.0, boss=True, states=gun,
        parts=(Part("left", arm, -0.3, 0.0), Part("right", arm, 0.3, 0.0)),
    )  # fmt: skip
    return Enemy.from_spec(spec, 0.0, 0.5)


def test_parts_join_with_the_enemy_follow_it_and_fire_from_where_they_are():
    boss = boss_with_arms()
    left, right = boss.parts
    assert (left.part_name, left.x, right.x) == ("left", -0.3, 0.3)
    boss.vx = 0.6
    created = boss.update(DT, TARGET, SCROLL)
    assert created[:2] == [left, right]
    assert left.x == pytest.approx(boss.x - 0.3)
    shots = bullets(run(boss, 0.5))
    assert shots and all(shot.x < boss.x for shot in shots)  # from the left part
    left.alive = False
    assert bullets(run(boss, 0.5)) == []  # it's gone: its gun is silent
    assert boss.wreckage() == [right]


def test_parts_cover_the_columns_under_them_and_count_in_its_health():
    boss = boss_with_arms()
    left, _ = boss.parts
    assert boss.covered(-0.3) and not boss.covered(0.0)
    assert boss.health_fraction == 1.0
    left.health = 0.0
    left.alive = False
    assert boss.health_fraction == pytest.approx(30 / 40)
    assert not boss.covered(-0.3)


def test_an_exit_can_wait_for_parts_or_lost_health():
    boss = boss_with_arms()
    spec = parse_enemy(
        "core",
        {"states": [{"name": "a", "exits": [{"to": "b", "parts": ["left"]}, {"to": "c", "health_below": 0.5}]}, {"name": "b"}, {"name": "c"}]},
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


def test_entering_from_a_side():
    crosser = described({"side_entry": True, "side_speed": 0.2})
    crosser.enter_from_side(-1)
    assert crosser.vx == pytest.approx(-0.2 * config.WIDTH_SCALE) and crosser.heading == math.pi
    steering = described({"side_entry": True})
    steering.enter_from_side(1)
    assert steering.vx == 0.0 and steering.heading == 0.0


def test_its_model_turns_as_described_or_as_its_state_says():
    diver = Enemy.of_kind("diver")
    assert diver.facing == "" and not diver.faces_travel
    diver.go_to("dive")
    assert diver.faces_travel
    assert Enemy.of_kind("turret").facing == "player"


def test_made_on_its_way_or_with_another_first_timer():
    shell = Enemy.of_kind("cluster_bomb", 0.0, 0.5, heading=1.0, timer=0.1)
    assert shell.heading == 1.0
    run(shell, 0.15)
    assert not shell.alive  # burst early
