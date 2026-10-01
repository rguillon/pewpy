"""Level data: loading and validating the JSON files in `src/pewpy/levels/`.

Levels are grouped in worlds (in the menus): `levels/world_<number>/` holds `world.json` (the world's name) and
`level_<number>.json` for each of its levels.
"""

import json
from dataclasses import dataclass, fields
from typing import Any

from pewpy.data import data_folder
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.roster import ENEMY_TYPES
from pewpy.scenery.background import BACKGROUNDS
from pewpy.scenery.terrain import GROUND_VOXEL

FORMATIONS = frozenset({"line", "column"})
TIMES_OF_DAY = frozenset({"day", "dusk", "night"})  # tints the ground and its haze, see background_view.py
SIDES = frozenset({"left", "right"})


class LevelError(Exception):
    def __init__(self, source: str, problem: str) -> None:
        super().__init__(f"{source}: {problem}")


@dataclass(frozen=True)
class Wave:
    """A group of enemies entering the screen.

    Most enemies enter from the top at `x`. Side-entry enemies (swarmer, mine_layer) enter from `side`
    ("left" or "right") at height `y`. `enemy` can also be a boss (a key of boss_catalog.BOSSES), which comes down from
    the top at `x`.

    Formations:
        line: `count` enemies side by side at the same time, `spacing` apart, centered on `x`
            (on `y` for side entries).
        column: `count` enemies at the same place, one every `interval` seconds.
    """

    time: float
    enemy: str = "drone"
    count: int = 1
    formation: str = "column"
    x: float = 0.0
    y: float = 0.5
    side: str = "left"
    spacing: float = 0.2
    interval: float = 0.5


@dataclass(frozen=True)
class Spawn:
    time: float
    enemy: str
    x: float
    y: float
    side: str


@dataclass(frozen=True)
class Level:
    name: str
    scroll_speed: float
    waves: tuple[Wave, ...]
    background: str = "space"  # one of background.BACKGROUNDS
    ground_voxel: float = GROUND_VOXEL  # size of the ground's voxels (planet background)
    time_of_day: str = "day"
    background_seed: int | None = None  # the background's layout (and colors, in space); None: different each time
    clouds: float = 0.0  # see-through clouds over the ground, from 0 (none) to 1 (the most)

    def spawns(self) -> list[Spawn]:
        """Every enemy of the level, sorted by the time it enters the screen."""
        spawns = []
        for wave in self.waves:
            side_entry = wave.enemy in ENEMY_TYPES and ENEMY_TYPES[wave.enemy].side_entry
            for i in range(wave.count):
                time, x, y = wave.time, wave.x, wave.y
                if wave.formation == "line":
                    offset = (i - (wave.count - 1) / 2) * wave.spacing
                    if side_entry:
                        y += offset
                    else:
                        x += offset
                else:
                    time += i * wave.interval
                spawns.append(Spawn(time, wave.enemy, x, y, wave.side))
        return sorted(spawns, key=lambda spawn: spawn.time)


def parse_level(data: dict[str, Any], source: str = "level") -> Level:
    """Build a Level from decoded JSON, with readable errors for typos and bad values."""
    _check_keys(
        data,
        {"name", "scroll_speed", "background", "ground_voxel", "time_of_day", "background_seed", "clouds", "waves"},
        source,
    )
    clouds = float(data.get("clouds", 0.0))
    if not 0.0 <= clouds <= 1.0:
        raise LevelError(source, f"'clouds' must be from 0 to 1, not {clouds}")
    time_of_day = str(data.get("time_of_day", "day"))
    _check_choice(time_of_day, TIMES_OF_DAY, "time_of_day", source)
    seed = data.get("background_seed")
    background = str(data.get("background", "space"))
    _check_choice(background, frozenset(BACKGROUNDS), "background", source)
    waves = []
    wave_keys = {field.name for field in fields(Wave)}
    for index, wave_data in enumerate(data.get("waves", [])):
        where = f"{source}, wave {index + 1}"
        _check_keys(wave_data, wave_keys, where)
        if "time" not in wave_data:
            raise LevelError(where, "missing 'time'")
        try:
            wave = Wave(**wave_data)
        except TypeError as error:
            raise LevelError(where, str(error)) from error
        _check_choice(wave.enemy, {**ENEMY_TYPES, **BOSSES}, "enemy", where)
        _check_choice(wave.side, SIDES, "side", where)
        _check_choice(wave.formation, FORMATIONS, "formation", where)
        if wave.count < 1:
            raise LevelError(where, "'count' must be at least 1")
        waves.append(wave)
    return Level(
        name=str(data.get("name", source)),
        scroll_speed=float(data.get("scroll_speed", 0.2)),
        waves=tuple(waves),
        background=background,
        ground_voxel=float(data.get("ground_voxel", GROUND_VOXEL)),
        time_of_day=time_of_day,
        background_seed=None if seed is None else int(seed),
        clouds=clouds,
    )


@dataclass(frozen=True)
class LevelWorld:
    """A world of the menus: a name and its levels (not world.World, which is a level being played)."""

    name: str
    levels: tuple[Level, ...]


def load_worlds() -> list[LevelWorld]:
    """Load every `world_<number>/` folder, in number order, with its levels in number order."""
    folder = data_folder() / "levels"
    worlds = sorted(
        (item for item in folder.iterdir() if item.name.startswith("world_")), key=lambda item: _number(item.name)
    )
    loaded = []
    for world in worlds:
        name = json.loads((world / "world.json").read_text())["name"]
        files = sorted(
            (file for file in world.iterdir() if file.name.startswith("level_")), key=lambda item: _number(item.name)
        )
        source = world.name + "/"
        loaded.append(
            LevelWorld(name, tuple(parse_level(json.loads(file.read_text()), source + file.name) for file in files))
        )
    return loaded


def load_levels() -> list[Level]:
    """Every level of every world, in order."""
    return [level for world in load_worlds() for level in world.levels]


def _number(name: str) -> int:
    """The number in `world_3` or `level_12.json`."""
    return int(name.split("_", 1)[1].removesuffix(".json"))


def _check_keys(data: dict[str, Any], allowed: set[str], source: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise LevelError(source, f"unknown keys {sorted(unknown)}, expected some of {sorted(allowed)}")


def _check_choice(value: str, choices: frozenset[str] | dict[str, Any], name: str, source: str) -> None:
    if value not in choices:
        raise LevelError(source, f"unknown {name} {value!r}, expected one of {sorted(choices)}")
