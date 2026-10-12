import re
from dataclasses import dataclass
from typing import Any

import pytest

from pewpy.scenery.params.reader import DEPENDS_ON, _convert, build, merge
from pewpy.scenery.params.types import Color3, SceneryError


@dataclass(frozen=True)
class Thing:
    name: str
    count: int
    size: float
    color: Color3
    sizes: tuple[float, ...]
    knobs: dict[str, float]
    anything: Any
    maybe: float | None


GOOD = {
    "name": "rock",
    "count": 3,
    "size": 1,
    "color": [1, 0.5, 0],
    "sizes": [1, 2, 3],
    "knobs": {"a": 1},
    "anything": [1, "two"],
    "maybe": None,
}


def test_a_level_changes_merge_over_its_preset_key_by_key() -> None:
    base = {"ground": {"depth": 0.5, "colors": {"a": [1, 1, 1], "b": [0, 0, 0]}}, "flora": None}
    over = {"ground": {"colors": {"a": [0, 0, 1]}}, "flora": {"kind": "palms"}}
    assert merge(base, over) == {
        "ground": {"depth": 0.5, "colors": {"a": [0, 0, 1], "b": [0, 0, 0]}},
        "flora": {"kind": "palms"},
    }


def test_naming_another_generator_takes_its_numbers_as_given() -> None:
    base = {"landscape": "mountains", "shape": {"range_size": 1.1}, "style": "mountains", "colors": {"rock": [0, 0, 0]}}
    assert merge(base, {"landscape": "badlands"}) == {**base, "landscape": "badlands", "shape": {}}
    assert merge(base, {"landscape": "mountains", "shape": {"crest_size": 0.5}})["shape"] == {
        "range_size": 1.1,
        "crest_size": 0.5,
    }
    assert DEPENDS_ON["style"] == ("colors",)


def test_a_dataclass_is_built_from_decoded_json() -> None:
    assert build(Thing, GOOD) == Thing("rock", 3, 1.0, (1.0, 0.5, 0.0), (1.0, 2.0, 3.0), {"a": 1.0}, [1, "two"], None)


def test_fields_can_be_given_rather_than_read() -> None:
    assert build(Thing, {key: value for key, value in GOOD.items() if key != "name"}, given={"name": "x"}).name == "x"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"colour": [0, 0, 0]}, "thing: unknown keys ['colour']"),
        ({"color": [0, 0]}, "thing.color: expected 3 values, not 2"),
        ({"color": "blue"}, "thing.color: expected a list"),
        ({"count": 1.5}, "thing.count: expected a whole number"),
        ({"count": True}, "thing.count: expected a whole number"),
        ({"size": "big"}, "thing.size: expected a number"),
        ({"size": False}, "thing.size: expected a number"),
        ({"name": 3}, "thing.name: expected a name"),
        ({"size": None}, "thing.size: missing (null)"),
        ({"knobs": [1]}, "thing.knobs: expected an object"),
        ({"sizes": [1, "two"]}, "thing.sizes[1]: expected a number"),
        ({"maybe": "x"}, "thing.maybe: expected a number"),
    ],
)
def test_mistakes_are_reported_with_where_they_are(changes: dict[str, Any], message: str) -> None:
    with pytest.raises(SceneryError, match=re.escape(message)):
        build(Thing, GOOD | changes, "thing")


def test_missing_fields_and_what_isnt_an_object_are_reported() -> None:
    with pytest.raises(SceneryError, match=re.escape("missing ['size']")):
        build(Thing, {key: value for key, value in GOOD.items() if key != "size"})
    with pytest.raises(SceneryError, match=re.escape("thing: expected an object")):
        build(Thing, [1], "thing")


def test_a_type_the_reader_does_not_know_is_reported() -> None:
    with pytest.raises(SceneryError, match=re.escape("can't read a <class 'bytes'>")):
        _convert(bytes, "x", "ground.depth")
