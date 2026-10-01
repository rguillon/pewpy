import pytest

from pewpy.scenery import params
from pewpy.scenery.params import SceneryError, merge, resolve


def test_every_preset_is_complete_and_checked():
    for name in params.backgrounds():
        scenery = resolve(name)
        assert scenery.name == name
    assert "default" not in params.backgrounds()


def test_presets_draw_what_they_have():
    space, debris, city = resolve("space"), resolve("debris"), resolve("city")
    assert space.stars and space.nebulas and space.planet and not space.ground
    assert debris.stars and debris.rocks and not debris.nebulas
    assert city.ground and city.settlement and not city.stars


def test_a_level_changes_merge_over_its_preset_key_by_key():
    base = {"ground": {"depth": 0.5, "colors": {"a": [1, 1, 1], "b": [0, 0, 0]}}, "flora": None}
    over = {"ground": {"colors": {"a": [0, 0, 1]}}, "flora": {"kind": "palms"}}
    assert merge(base, over) == {
        "ground": {"depth": 0.5, "colors": {"a": [0, 0, 1], "b": [0, 0, 0]}},
        "flora": {"kind": "palms"},
    }


def test_a_change_reaches_the_scenery():
    scenery = resolve("desert", {"haze": {"amount": 0.1}, "ground": {"shape": {"dune_spacing": 0.8}}})
    assert scenery.haze.amount == 0.1
    assert scenery.haze.color == resolve("desert").haze.color  # the rest stays
    assert scenery.ground is not None and scenery.ground.shape["dune_spacing"] == 0.8


def test_naming_another_landscape_takes_its_own_numbers_not_the_old_ones():
    scenery = resolve("ocean", {"ground": {"landscape": "clouds", "shape": {"cover": 0.5, "size": 0.9}}})
    assert scenery.ground is not None
    assert scenery.ground.shape == {"cover": 0.5, "size": 0.9}
    ocean = resolve("ocean").ground
    assert ocean is not None
    assert scenery.ground.colors == ocean.colors  # the painter is the same: its colors stay


def test_a_ground_can_be_given_to_a_preset_without_one():
    city = resolve("city")
    assert city.ground is not None
    scenery = resolve("space", {"ground": {**params.presets()["planet"]["ground"]}})
    assert scenery.ground is not None and scenery.ground.landscape == "hills"


@pytest.mark.parametrize(
    ("background", "changes", "message"),
    [
        ("jungle", {}, "unknown background 'jungle'"),
        ("default", {}, "unknown background 'default'"),
        ("space", {"skye": [0, 0, 0]}, "unknown keys ['skye']"),
        ("space", {"sky": [0, 0]}, "space.sky: expected 3 values, not 2"),
        ("space", {"sky": "blue"}, "space.sky: expected a list"),
        ("debris", {"rocks": {"spin": True}}, "debris.rocks.spin: expected a number"),
        ("space", {"stars": {"count": 1.5}}, "space.stars.count: expected a whole number"),
        ("ocean", {"ground": {"landscape": "lakes"}}, "unknown 'lakes'"),
        ("ocean", {"ground": {"landscape": "clouds", "shape": {"cover": 0.5}}}, "missing ['size']"),
        ("forest", {"ground": {"colors": {"tree_d": [0, 0, 0]}}}, "unknown ['tree_d']"),
        ("city", {"settlement": {"kind": "village"}}, "unknown 'village'"),
        ("ocean", {"fluid": {"kind": "lava"}}, "missing ['crust', 'hot']"),
    ],
)
def test_mistakes_are_reported_with_where_they_are(background, changes, message):
    with pytest.raises(SceneryError, match=message.replace("[", r"\[").replace("]", r"\]")):
        resolve(background, changes)


def test_every_style_and_settlement_lists_its_colors():
    from pewpy.scenery import ground_shader, settlement

    assert set(params.STYLE_COLORS) >= set(ground_shader.STYLES)
    assert set(params.SURFACE_COLORS) == set(settlement.SETTLEMENTS)
    for names in params.SURFACE_COLORS.values():
        assert set(names) <= set(ground_shader.SURFACE_SLOTS)
    assert all(len(names) <= ground_shader.PALETTE_SIZE for names in params.STYLE_COLORS.values())
