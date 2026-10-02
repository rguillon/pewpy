from typing import Any

import pytest

from pewpy.game.enemies.roster import ENEMY_TYPES
from pewpy.game.level import Level, LevelError, Wave, load_levels, load_worlds, parse_level
from pewpy.scenery import params

GROUNDS = [name for name in params.backgrounds() if params.resolve(name).ground is not None]


def test_bundled_levels_load_as_eight_worlds_of_six() -> None:
    worlds = load_worlds()
    assert [world.name for world in worlds] == [
        "Highlands",
        "Wildwood",
        "Fenlands",
        "Heartland",
        "Archipelago",
        "Steamvale",
        "Ironworks",
        "Metropolis",
    ]
    assert all(len(world.levels) == 6 for world in worlds)
    levels = load_levels()
    assert levels == [level for world in worlds for level in world.levels]
    assert all(level.spawns() for level in levels)
    assert len({level.name for level in levels}) == 48


def test_the_levels_of_the_spec_keep_their_places_in_the_worlds() -> None:
    worlds = load_worlds()
    assert worlds[0].levels[0].name == "High Peaks"  # 1-1
    assert worlds[0].levels[5].name == "Summit"  # 1-6
    assert worlds[1].levels[0].name == "Greenwood"  # 2-1
    assert worlds[7].levels[5].name == "The Core"  # 8-6


def test_line_formation_spawns_side_by_side_at_once() -> None:
    level = Level("test", 0.2, (Wave(time=2.0, count=3, formation="line", x=0.1, spacing=0.2),))
    spawns = level.spawns()
    assert [spawn.time for spawn in spawns] == [2.0, 2.0, 2.0]
    assert [spawn.x for spawn in spawns] == pytest.approx([-0.1, 0.1, 0.3])


def test_column_formation_spawns_one_after_another() -> None:
    level = Level("test", 0.2, (Wave(time=1.0, count=3, formation="column", x=-0.2, interval=0.5),))
    spawns = level.spawns()
    assert [spawn.time for spawn in spawns] == [1.0, 1.5, 2.0]
    assert {spawn.x for spawn in spawns} == {-0.2}


def test_spawns_are_sorted() -> None:
    level = Level("test", 0.2, (Wave(time=5.0), Wave(time=1.0, count=20, formation="line", spacing=0.3)))
    spawns = level.spawns()
    assert spawns == sorted(spawns, key=lambda spawn: spawn.time)


def test_side_entry_line_spreads_vertically() -> None:
    level = Level("test", 0.2, (Wave(time=1.0, enemy="swarmer", count=3, formation="line", y=0.4, side="right"),))
    spawns = level.spawns()
    assert [spawn.y for spawn in spawns] == pytest.approx([0.2, 0.4, 0.6])
    assert {spawn.side for spawn in spawns} == {"right"}


def test_parse_level() -> None:
    level = parse_level({
        "name": "Test",
        "scroll_speed": 0.5,
        "waves": [{"time": 3, "count": 2, "formation": "line"}],
    })
    assert level == Level("Test", 0.5, (Wave(time=3, count=2, formation="line"),))
    assert level.background == "space"  # the default


def test_parse_level_background() -> None:
    assert parse_level({"background": "debris"}).background == "debris"
    assert parse_level({"background": "city"}).background == "city"
    assert parse_level({"background": "ocean"}).background == "ocean"


def test_each_world_keeps_to_its_ground() -> None:
    grounds = ["mountains", "forest", "swamp", "farmland", "ocean", "geysers", "refinery", "city"]
    for world, ground in zip(load_worlds(), grounds, strict=True):
        assert {level.background for level in world.levels} == {ground}


def test_levels_of_a_world_vary() -> None:
    for world in load_worlds():
        looks = {
            (level.time_of_day, level.background_seed, level.clouds, repr(level.scenery)) for level in world.levels
        }
        assert len(looks) == len(world.levels)  # no two levels look the same


def test_parse_level_clouds() -> None:
    assert parse_level({"clouds": 0.4}).clouds == 0.4
    assert parse_level({}).clouds == 0.0
    with pytest.raises(LevelError, match="'clouds' must be from 0 to 1"):
        parse_level({"clouds": 1.5})


def test_each_world_has_clouds_some_levels_more_than_others() -> None:
    for world in load_worlds():
        amounts = [level.clouds for level in world.levels]
        assert min(amounts) <= 0.2, world.name  # nearly clear...
        assert max(amounts) >= 0.8, world.name  # ...to heavy


def test_parse_level_time_of_day_and_background_seed() -> None:
    level = parse_level({"time_of_day": "dusk", "background_seed": 12})
    assert (level.time_of_day, level.background_seed) == ("dusk", 12)
    assert parse_level({}).time_of_day == "day"


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"nmae": "typo"}, "unknown keys ['nmae']"),
        ({"waves": [{"count": 2}]}, "wave 1: missing 'time'"),
        ({"waves": [{"time": 1, "cuont": 2}]}, "wave 1: unknown keys ['cuont']"),
        ({"waves": [{"time": 1, "enemy": "dragon"}]}, "unknown enemy 'dragon'"),
        ({"waves": [{"time": 1, "formation": "circle"}]}, "unknown formation 'circle'"),
        ({"waves": [{"time": 1}, {"time": 2, "count": 0}]}, "wave 2: 'count' must be at least 1"),
        ({"background": "jungle"}, "unknown background 'jungle'"),
        ({"time_of_day": "noon"}, "unknown time_of_day 'noon'"),
        ({"background": "ocean", "scenery": {"fluid": {"colours": {}}}}, "ocean.fluid: unknown keys ['colours']"),
        ({"background": "city", "scenery": {"ground": {"depth": "deep"}}}, "city.ground.depth: expected a number"),
    ],
)
def test_parse_level_reports_mistakes(data: dict[str, Any], message: str) -> None:
    with pytest.raises(LevelError, match=message.replace("[", r"\[").replace("]", r"\]")):
        parse_level(data, "level_9.json")


def test_a_level_can_change_its_scenery() -> None:
    level = parse_level({"background": "ocean", "scenery": {"fluid": {"colors": {"deep": [0.1, 0.0, 0.0]}}}})
    look = level.scenery_params()
    assert look.fluid is not None
    assert look.fluid.colors["deep"] == (0.1, 0.0, 0.0)
    preset = parse_level({"background": "ocean"}).scenery_params().fluid
    assert preset is not None
    assert look.fluid.colors["foam"] == preset.colors["foam"]  # the rest stays


def test_every_level_has_a_complete_scenery() -> None:
    for level in load_levels():
        look = level.scenery_params()
        assert level.time_of_day in look.times_of_day


def test_levels_accept_bosses() -> None:
    level = parse_level({"name": "end", "waves": [{"time": 60, "enemy": "overmind"}]})
    assert level.spawns()[0].enemy == "overmind"


def test_every_level_is_on_a_ground_and_each_world_on_its_own() -> None:
    worlds = load_worlds()
    assert all(level.background in GROUNDS for world in worlds for level in world.levels)
    assert len({world.levels[0].background for world in worlds}) == len(worlds)


def test_no_ground_enemies_over_water_or_clouds() -> None:
    # Turrets, tanks and the like are on the ground: they would look odd on the sea, the ice floes or the clouds.
    for level in load_levels():
        if level.background in ("pack_ice", "swamp", "clouds", "ocean"):
            ground = [
                wave.enemy for wave in level.waves if wave.enemy in ENEMY_TYPES and ENEMY_TYPES[wave.enemy].ground
            ]
            assert ground == [], level.name


def test_a_wave_with_an_unknown_key_says_so() -> None:
    with pytest.raises(LevelError, match="speed"):
        parse_level({"waves": [{"time": 1, "speed": 2}]})
