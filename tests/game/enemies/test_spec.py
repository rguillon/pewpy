from typing import Any

import pytest

from pewpy import config
from pewpy.game.enemies.actions import Fire, Sway, Velocity
from pewpy.game.enemies.exits import BelowY, Cycle, Parts
from pewpy.game.enemies.motions import Bounce
from pewpy.game.enemies.spec import EnemySpec, EnemySpecError, Part, parse_enemy
from pewpy.game.weapons.guns import Gun


def test_an_enemy_is_read_with_its_states_guns_and_exits() -> None:
    spec = parse_enemy(
        "test",
        {
            "note": "for the people editing the file",
            "voxels": [10, 20],
            "velocity": [0.0, -0.3],
            "start": [{"type": "velocity", "vx": 0.1}],
            "states": [
                {
                    "name": "fly",
                    "motions": [{"type": "bounce"}],
                    "guns": [
                        {"pattern": "fan", "interval": 1.0, "speed": 0.5,
                         "angles": [-10, 10], "origins": [["0.5w", 0]]},
                        {"from": "gun", "pattern": "fan", "interval": 1.0, "speed": 0.0,
                         "velocities": [[0.1, -0.2]]},
                        {"pattern": "fan", "interval": 1.0, "speed": 0.0,
                         "sequence": [{"pattern": "ring", "count": 4}]},
                    ],
                    "exits": [
                        {"to": "fly", "cycle": [2.0, 0.0, 1.0], "parts": ["gun"]},
                        {"to": "fly", "timer": True,
                         "then": [{"type": "fire", "gun": {"pattern": "fan", "interval": 0, "speed": 0.4}}]},
                    ],
                }
            ],
            "on_destroyed": [{"kind": "swarmer", "heading": -90}],
        },
        "test",
    )  # fmt: skip
    assert (spec.width, spec.height) == pytest.approx((10 * config.MODEL_VOXEL, 20 * config.MODEL_VOXEL))
    assert spec.velocity == (0.0, -0.3)
    assert spec.start == (Velocity(vx=0.1),)
    state = spec.states[0]
    (_, aimed), (source, straight), (_, cycling) = state.guns
    assert aimed.angles == (-10, 10)
    assert aimed.origins == (("0.5w", 0),)
    assert source == "gun"
    assert straight.velocities == ((0.1, -0.2),)
    assert cycling.sequence == (Gun("ring", 0.0, 0.0, count=4),)
    assert state.motions == (Bounce(),)
    assert state.exits[0].conditions == (Cycle(2.0, 0.0, 1.0), Parts(("gun",)))
    (fire,) = state.exits[1].then
    assert isinstance(fire, Fire)
    assert fire.gun.speed == 0.4
    assert spec.on_destroyed[0].kind == "swarmer"


def test_a_size_can_be_given_in_world_units() -> None:
    spec = parse_enemy("test", {"size": [0.2, 0.3]}, "test")
    assert (spec.width, spec.height) == (0.2, 0.3)


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"speed": 3}, "speed"),
        ({"states": [{"name": "a", "motions": [{"type": "teleport"}]}]}, "motion 'teleport'"),
        ({"states": [{"name": "a", "exits": [{"to": "b"}]}]}, "unknown state 'b'"),
        ({"start": [{"type": "explode"}]}, "action 'explode'"),
        ({"start": [{"type": "fire"}]}, "gun"),
        ({"states": [{"name": "a", "motions": [{"type": "bounce", "speed": 1}]}]}, "speed"),
        ({"states": [{"name": "a", "exits": [{"to": "a", "soon": True}]}]}, "exit condition 'soon'"),
        ({"states": [{"name": "a", "exits": [{"to": "a", "timer": False}]}]}, "timer can only be true"),
    ],
)
def test_mistakes_say_where_they_are(data: dict[str, Any], message: str) -> None:
    with pytest.raises(EnemySpecError, match=message):
        parse_enemy("test", data, "file.json: test")


def test_a_bosss_span_counts_its_parts() -> None:
    part = EnemySpec(kind="arm", width=0.2)
    spec = EnemySpec(kind="boss", width=0.4, parts=(Part("arm", part, 0.5, 0.0),))
    assert spec.half_span == pytest.approx(0.6)
    assert EnemySpec(kind="plain", width=0.4).half_span == pytest.approx(0.2)
    assert spec.state_index("idle") == 0


def test_a_boss_is_written_shortly_with_its_phases() -> None:
    spec = parse_enemy(
        "boss",
        {
            "boss": True,
            "size": [0.3, 0.2],
            "parts": [{"name": "arm", "x": 0.2, "y": 0.0, "size": [0.1, 0.1]}],
            "phases": [
                {"sway": 0.1, "armored": True, "until": {"parts": ["arm"]},
                 "guns": [{"from": "arm", "pattern": "fan", "interval": 2.0, "speed": 0.4}]},
                {"sway": 0.2, "guns": [{"pattern": "aimed", "interval": 1.0, "speed": 0.5}], "faces": "player"},
            ],
        },
        "test",
    )  # fmt: skip
    assert spec.boss
    assert not spec.rammable
    assert spec.parts[0].spec.drop_chance == pytest.approx(0.3)
    assert not spec.parts[0].spec.rammable
    enter, armored, rage = spec.states
    assert [state.name for state in spec.states] == ["enter", "phase 1", "phase 2"]
    assert enter.coming_in
    assert enter.exits[0].then == (Velocity(vy=0.0), Sway(0.1))
    assert not enter.vulnerable
    assert not armored.vulnerable
    assert armored.motions == (Bounce(clamp=True),)
    assert armored.exits[0].conditions == (Parts(("arm",)),)
    assert armored.exits[0].then == (Sway(0.2),)
    ((source, gun),) = armored.guns
    assert source == "arm"
    assert (gun.reload, gun.off_screen) == ("carry", "fire")
    assert rage.vulnerable
    assert rage.exits == ()
    assert rage.faces == "player"


def test_a_gun_from_several_parts_fires_from_each_in_turn() -> None:
    gun = {"from": ["a", "b", "c", "d"], "pattern": "fan", "interval": 2.0, "speed": 0.4, "delay": 0.1}
    for written in (
        {"phases": [{"sway": 0.1, "guns": [gun]}]},
        {"states": [{"name": "fly"}, {"name": "x", "guns": [gun]}]},
    ):
        guns = parse_enemy("boss", written, "test").states[1].guns
        assert [source for source, _ in guns] == ["a", "b", "c", "d"]
        assert [gun.delay for _, gun in guns] == pytest.approx([0.1, 0.6, 1.1, 1.6])


def test_any_enemy_can_have_phases_and_parts_without_the_bosses_usual_fields() -> None:
    spec = parse_enemy(
        "carrier",
        {
            "size": [0.2, 0.1],
            "velocity": [0.0, -0.4],
            "hold_y": 0.3,
            "phase_pause": 0.5,
            "parts": [{"name": "pod", "x": 0.1, "y": 0.0, "size": [0.05, 0.05]}],
            "phases": [
                {"sway": 0.1, "until": {"parts": ["pod"]},
                 "guns": [{"from": "pod", "pattern": "aimed", "interval": 1.0, "speed": 0.5}]},
                {"sway": 0.2},
            ],
        },
        "test",
    )  # fmt: skip
    assert not spec.boss
    assert spec.rammable
    assert spec.leaves_screen
    assert spec.velocity == (0.0, -0.4)
    assert spec.explosions == ()
    enter, first, _ = spec.states
    assert enter.coming_in
    assert enter.vulnerable
    assert enter.exits[0].conditions == (BelowY(0.3),)
    assert first.warmup == pytest.approx(0.5)
    ((_, gun),) = first.guns
    assert gun.reload != "carry"
    pod = spec.parts[0].spec
    assert (pod.placeable, pod.leaves_screen, pod.rammable, pod.drop_chance) == (False, False, True, 0.0)


def test_points_are_whole_numbers_even_written_with_a_point() -> None:
    spec = parse_enemy("test", {"points": 110.0, "parts": [{"name": "a", "x": 0, "y": 0, "points": 50.0}]}, "test")
    assert spec.points == 110
    assert isinstance(spec.points, int)
    assert isinstance(spec.parts[0].spec.points, int)
    with pytest.raises(EnemySpecError, match="whole number"):
        parse_enemy("test", {"points": 12.5}, "test")
