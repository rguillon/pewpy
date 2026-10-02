from typing import Any

import pytest

from pewpy import config
from pewpy.game.enemies.actions import Fire, Velocity
from pewpy.game.enemies.exits import Cycle, Parts
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
