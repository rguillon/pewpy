from typing import Any

import pytest

from pewpy.graphics.models.drawings.engines import FLAME_COLOR, Engine, parse_engines
from pewpy.graphics.models.drawings.errors import VoxelDrawingError

ENGINE = {"x": 1, "y": 1, "width": 1, "length": 4, "towards": "bottom"}


def test_a_drawing_can_have_engines() -> None:
    engines = parse_engines({"rows": ["a"], "engines": [ENGINE, {**ENGINE, "color": [1, 0.5, 0]}]})
    assert engines[0] == Engine(1.0, 1.0, 1.0, 4.0, "bottom", FLAME_COLOR)
    assert engines[1].color == (1.0, 0.5, 0.0, 1.0)
    assert parse_engines({"rows": ["a"]}) == []
    assert parse_engines(["not", "a", "drawing"]) == []


def test_an_engine_can_sit_above_the_middle_plane() -> None:
    engine = parse_engines(
        {"rows": ["a"], "engines": [{"x": 0, "y": 0, "width": 1, "length": 1, "towards": "top", "z": 2}]}, "ship.json"
    )[0]
    assert engine.z == 2.0


@pytest.mark.parametrize(
    ("engine", "problem"),
    [
        ({"x": 1, "y": 1}, "expected the keys"),
        ({**ENGINE, "towards": "left"}, "'towards' must be one of"),
        ({**ENGINE, "length": 0}, "more than 0"),
        ({**ENGINE, "x": "1"}, "must be numbers"),
        ({**ENGINE, "color": [2, 0, 0]}, "3 numbers from 0 to 1"),
        ({**ENGINE, "z": "up"}, "'z' must be a number"),
    ],
)
def test_malformed_engines_say_what_is_wrong(engine: dict[str, Any], problem: str) -> None:
    with pytest.raises(VoxelDrawingError, match=problem):
        parse_engines({"rows": ["a"], "engines": [engine]}, "broken.json")


def test_engines_must_be_a_list() -> None:
    with pytest.raises(VoxelDrawingError, match="must be a list"):
        parse_engines({"rows": ["a"], "engines": {}}, "ship.json")
