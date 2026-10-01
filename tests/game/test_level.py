import pytest

from pewpy.game.level import Level, LevelError, Wave, load_levels, load_worlds, parse_level


def test_bundled_levels_load_as_five_worlds_of_eight():
    worlds = load_worlds()
    assert [world.name for world in worlds] == ["Orbit", "Heartland", "Waters", "Badlands", "Metropolis"]
    assert all(len(world.levels) == 8 for world in worlds)
    levels = load_levels()
    assert levels == [level for world in worlds for level in world.levels]
    assert all(level.spawns() for level in levels)
    assert len({level.name for level in levels}) == 40


def test_the_levels_of_the_spec_keep_their_places_in_the_worlds():
    worlds = load_worlds()
    assert worlds[0].levels[0].name == "Outer Belt"  # 1-1
    assert worlds[0].levels[7].name == "Minefield"  # 1-8
    assert worlds[1].levels[0].name == "Ground Defense"  # 2-1


def test_line_formation_spawns_side_by_side_at_once():
    level = Level("test", 0.2, (Wave(time=2.0, count=3, formation="line", x=0.1, spacing=0.2),))
    spawns = level.spawns()
    assert [spawn.time for spawn in spawns] == [2.0, 2.0, 2.0]
    assert [spawn.x for spawn in spawns] == pytest.approx([-0.1, 0.1, 0.3])


def test_column_formation_spawns_one_after_another():
    level = Level("test", 0.2, (Wave(time=1.0, count=3, formation="column", x=-0.2, interval=0.5),))
    spawns = level.spawns()
    assert [spawn.time for spawn in spawns] == [1.0, 1.5, 2.0]
    assert {spawn.x for spawn in spawns} == {-0.2}


def test_spawns_are_sorted():
    level = Level("test", 0.2, (Wave(time=5.0), Wave(time=1.0, count=20, formation="line", spacing=0.3)))
    spawns = level.spawns()
    assert spawns == sorted(spawns, key=lambda spawn: spawn.time)


def test_side_entry_line_spreads_vertically():
    level = Level("test", 0.2, (Wave(time=1.0, enemy="swarmer", count=3, formation="line", y=0.4, side="right"),))
    spawns = level.spawns()
    assert [spawn.y for spawn in spawns] == pytest.approx([0.2, 0.4, 0.6])
    assert {spawn.side for spawn in spawns} == {"right"}


def test_parse_level():
    level = parse_level({
        "name": "Test",
        "scroll_speed": 0.5,
        "waves": [{"time": 3, "count": 2, "formation": "line"}],
    })
    assert level == Level("Test", 0.5, (Wave(time=3, count=2, formation="line"),))
    assert level.background == "space"  # the default


def test_parse_level_background():
    assert parse_level({"background": "debris"}).background == "debris"
    assert parse_level({"background": "planet", "ground_voxel": 0.02}).ground_voxel == 0.02
    assert parse_level({"background": "city"}).background == "city"
    assert parse_level({"background": "ocean"}).background == "ocean"


def test_each_world_keeps_to_its_style():
    styles = {
        "Orbit": {"space", "debris"},
        "Heartland": {"planet", "farmland", "forest", "swamp"},
        "Waters": {"ocean", "pack_ice", "clouds"},
        "Badlands": {"desert", "canyon", "volcano", "mountains"},
        "Metropolis": {"city", "refinery"},
    }
    for world in load_worlds():
        backgrounds = [level.background for level in world.levels]
        assert set(backgrounds) == styles[world.name]  # uses all of its grounds, and only those


def test_levels_of_a_world_vary():
    for world in load_worlds():
        looks = {(level.background, level.time_of_day, level.background_seed) for level in world.levels}
        assert len(looks) == 8  # no two levels look the same


def test_parse_level_clouds():
    assert parse_level({"clouds": 0.4}).clouds == 0.4
    assert parse_level({}).clouds == 0.0
    with pytest.raises(LevelError, match="'clouds' must be from 0 to 1"):
        parse_level({"clouds": 1.5})


def test_atmosphere_levels_have_clouds_some_more_than_others():
    worlds = load_worlds()
    assert all(level.clouds == 0 for level in worlds[0].levels)  # space
    for world in worlds[1:]:
        amounts = [level.clouds for level in world.levels]
        assert min(amounts) <= 0.2 and max(amounts) >= 0.8, world.name  # nearly clear to heavy


def test_parse_level_time_of_day_and_background_seed():
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
    ],
)
def test_parse_level_reports_mistakes(data, message):
    with pytest.raises(LevelError, match=message.replace("[", r"\[").replace("]", r"\]")):
        parse_level(data, "level_9.json")
