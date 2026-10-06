import re
from typing import Any

import pytest

from pewpy.scenery import params
from pewpy.scenery.ground import kinds, shader
from pewpy.scenery.params import SceneryError, merge, reader, resolve

GROUNDS = [name for name in params.backgrounds() if params.resolve(name).ground is not None]


def test_every_preset_is_complete_and_checked() -> None:
    for name in params.backgrounds():
        scenery = resolve(name)
        assert scenery.name == name
    assert "default" not in params.backgrounds()


def test_presets_draw_what_they_have() -> None:
    space, city = resolve("space"), resolve("city")
    assert space.stars
    assert space.nebulas
    assert space.planet
    assert not space.ground
    assert city.ground
    assert city.settlement
    assert not city.stars


def test_a_level_changes_merge_over_its_preset_key_by_key() -> None:
    base = {"ground": {"depth": 0.5, "colors": {"a": [1, 1, 1], "b": [0, 0, 0]}}, "flora": None}
    over = {"ground": {"colors": {"a": [0, 0, 1]}}, "flora": {"kind": "palms"}}
    assert merge(base, over) == {
        "ground": {"depth": 0.5, "colors": {"a": [0, 0, 1], "b": [0, 0, 0]}},
        "flora": {"kind": "palms"},
    }


def test_a_change_reaches_the_scenery() -> None:
    scenery = resolve("savanna", {"haze": {"amount": 0.1}, "ground": {"shape": {"bend_spacing": 0.8}}})
    assert scenery.haze.amount == 0.1
    assert scenery.haze.color == resolve("savanna").haze.color  # the rest stays
    assert scenery.ground is not None
    assert scenery.ground.shape["bend_spacing"] == 0.8


def test_naming_another_landscape_takes_its_own_numbers_not_the_old_ones() -> None:
    scenery = resolve("salt_pan", {"ground": {"landscape": "badlands", "shape": {"size": 0.5, "floor": 0.2}}})
    assert scenery.ground is not None
    assert scenery.ground.shape == {"size": 0.5, "floor": 0.2}
    salt_pan = resolve("salt_pan").ground
    assert salt_pan is not None
    assert scenery.ground.colors == salt_pan.colors  # the painter is the same: its colors stay


def test_a_ground_can_be_given_to_a_preset_without_one() -> None:
    city = resolve("city")
    assert city.ground is not None
    scenery = resolve("space", {"ground": {**params.presets()["savanna"]["ground"]}})
    assert scenery.ground is not None
    assert scenery.ground.landscape == "savanna"


@pytest.mark.parametrize(
    ("background", "changes", "message"),
    [
        ("jungle", {}, "unknown background 'jungle'"),
        ("default", {}, "unknown background 'default'"),
        ("space", {"skye": [0, 0, 0]}, "unknown keys ['skye']"),
        ("space", {"sky": [0, 0]}, "space.sky: expected 3 values, not 2"),
        ("space", {"sky": "blue"}, "space.sky: expected a list"),
        ("space", {"stars": {"count": 1.5}}, "space.stars.count: expected a whole number"),
        ("salt_pan", {"ground": {"landscape": "lakes"}}, "unknown 'lakes'"),
        ("salt_pan", {"ground": {"landscape": "badlands", "shape": {"size": 0.5}}}, "missing ['floor']"),
        ("forest", {"ground": {"colors": {"tree_d": [0, 0, 0]}}}, "unknown ['tree_d']"),
        ("city", {"settlement": {"kind": "village"}}, "unknown 'village'"),
        ("salt_pan", {"fluid": {"kind": "lava"}}, "unknown 'lava'"),
        ("space", {"sky": None}, "space.sky: missing (null)"),
        ("forest", {"ground": {"colors": [1]}}, "forest.ground.colors: expected an object"),
        ("space", {"stars": 3}, "space.stars: expected an object"),
        ("salt_pan", {"stars": {"count": 3}}, "salt_pan.stars: missing ['depth', 'layers']"),
        ("forest", {"ground": {"style": "chalk"}}, "unknown 'chalk'"),
        ("city", {"settlement": {"kind": 3}}, "city.settlement.kind: expected a name"),
    ],
)
def test_mistakes_are_reported_with_where_they_are(background: str, changes: dict[str, Any], message: str) -> None:
    with pytest.raises(SceneryError, match=re.escape(message)):
        resolve(background, changes)


def test_a_type_the_reader_does_not_know_is_reported() -> None:
    with pytest.raises(SceneryError, match=re.escape("can't read a <class 'bytes'>")):
        reader._convert(bytes, "x", "ground.depth")


def test_every_style_and_settlement_lists_its_colors() -> None:
    assert set(params.STYLE_COLORS) >= set(shader.STYLES)
    assert set(params.SURFACE_COLORS) == set(kinds.SETTLEMENTS)
    for names in params.SURFACE_COLORS.values():
        assert set(names) <= set(shader.SURFACE_SLOTS)
    assert all(len(names) <= shader.PALETTE_SIZE for names in params.STYLE_COLORS.values())


@pytest.mark.parametrize("name", GROUNDS)
def test_every_ground_stays_behind_the_ships(name: str) -> None:
    ground = params.resolve(name).ground
    assert ground is not None
    assert ground.depth - ground.max_height > 0.1  # the ships fly at depth 0 and are about 0.1 deep
