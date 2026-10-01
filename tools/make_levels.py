"""Generate the game's levels (src/pewpy/levels/) from the plan of the worlds below (03-levels.md).

    make levels                        # every world, the same levels every time
    make levels ARGS="--seed 1234"     # another draw of the waves (the looks and the bosses stay)

(or `uv run python -m tools.make_levels ...`).

Each world keeps one ground (one background preset) on all its levels; its levels only change that ground's
numbers: time of day, clouds, haze, layout seed, the preset's shape and layout knobs, a few colors. Each level has
a difficulty: level L of world W is 2 (W - 1) + L, so a world's first level is as hard as the level 3 of the world
before. The difficulty sets the scroll speed, the size of the groups, the level's threat (its enemies' points, spread
over about 48 s: the harder, the denser) and which enemies come (each enemy has the difficulty it unlocks at).
A level: a warm-up wave, the main waves, then a finale of its signature enemies close together, and its boss 6 s
after the last wave.
"""

import argparse
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pewpy.game.roster import ENEMY_TYPES

LEVELS = Path(__file__).resolve().parent.parent / "src" / "pewpy" / "levels"
DEFAULT_SEED = 2024

# Difficulty: 1 (the first level) to 20 (the last one).
MAX_DIFFICULTY = 20
SCROLL_SPEED = (0.2, 0.31)  # at the easiest and the hardest level
THREAT = (8600, 22500)  # a level's enemies, in points, at the easiest and the hardest level...
THREAT_CURVE = 0.6  # ...rising fast at first, then slower
GROWTH = 1.073  # groups are this much bigger for each step of difficulty
KINDS = (6, 17)  # how many kinds of enemies a level sends
LEVEL_TIME = 48.0  # seconds of waves (the boss comes after)
TWIN_WAVES = (0.15, 0.35)  # the share of waves sent together with the one before
MIN_GAP = 0.8  # seconds between waves, at least
FINALE_SHARE = 0.2  # the last part of the threat: the signature enemies...
FINALE_PACE = 0.6  # ...closer together
BOSS_DELAY = 6.0
LINE_SPAN = 2.1  # a line of enemies across the screen is at most this wide (the play area is 2.5)
SIDE_SPAN = 1.0  # ...and a line coming in from a side at most this tall
WARM_UP = ("drone", "weaver", "dart", "mite")  # easy first waves
GROUND = frozenset({"turret", "flak_cannon", "tank", "rocket_truck", "missile_silo"})  # roll on the ground

# The difficulty each enemy first comes at.
UNLOCK = {
    "dart": 1,
    "diver": 1,
    "drone": 1,
    "gunship": 1,
    "mite": 1,
    "weaver": 1,
    "imp": 2,
    "rocketeer": 2,
    "sniper": 2,
    "spark": 2,
    "swarmer": 2,
    "tick": 2,
    "hornet": 3,
    "serpent": 3,
    "catamaran": 3,
    "albatross": 4,
    "buckshot": 4,
    "mine_layer": 5,
    "shield_carrier": 5,
    "splitter": 5,
    "turret": 5,
    "flak_cannon": 5,
    "hunter": 5,
    "kestrel": 5,
    "stalker": 5,
    "missile_silo": 6,
    "rapier": 6,
    "scrapper": 6,
    "outrider": 6,
    "tank": 6,
    "bomber": 7,
    "needle": 7,
    "wisp": 7,
    "freighter": 7,
    "rocket_truck": 7,
    "lancer": 9,
    "manta": 9,
    "broadside": 10,
    "javelin": 10,
    "harrier": 10,
    "brood": 11,
    "brawler": 11,
    "howitzer": 12,
    "rampart": 13,
    "condor": 14,
    "warhawk": 15,
    "stormcrow": 17,
    "pincer": 18,
    "behemoth": 18,
}

# How each enemy's groups come (a wave without its time and enemy); `count` is the group's size at difficulty 1,
# multiplied by GROWTH for each step above it.
SHAPES: dict[str, tuple[dict[str, Any], ...]] = {
    "albatross": (
        {"x": -0.33, "count": 0.84},
        {"x": 0.33, "count": 0.79},
    ),
    "behemoth": (
        {"x": 0.0, "count": 0.31},
        {"x": 0.33, "count": 0.28},
    ),
    "bomber": (
        {"formation": "column", "side": "right", "y": 0.66, "count": 0.68},
        {"formation": "column", "side": "right", "y": 0.74, "count": 0.49},
        {"formation": "column", "side": "left", "y": 0.59, "count": 0.49},
        {"formation": "column", "side": "left", "y": 0.65, "count": 0.42},
        {"formation": "column", "side": "right", "y": 0.59, "count": 0.41},
        {"formation": "column", "side": "right", "y": 0.65, "count": 0.38},
        {"formation": "column", "side": "left", "y": 0.6, "count": 0.37},
        {"formation": "column", "side": "right", "y": 0.68, "count": 0.33},
        {"formation": "column", "side": "left", "y": 0.67, "count": 0.32},
        {"formation": "column", "side": "left", "y": 0.58, "count": 0.31},
        {"formation": "column", "side": "left", "y": 0.69, "count": 0.28},
        {"formation": "column", "side": "left", "y": 0.71, "count": 0.26},
    ),
    "brawler": (
        {"x": -0.33, "count": 0.5},
        {"x": 0.5, "count": 0.41},
    ),
    "broadside": (
        {"formation": "column", "interval": 1.2, "side": "right", "y": 0.45, "count": 0.47},
        {"formation": "column", "interval": 1.2, "side": "left", "y": 0.45, "count": 0.36},
    ),
    "brood": (
        {"x": 0.33, "count": 0.52},
        {"x": 0.5, "count": 0.38},
    ),
    "buckshot": ({"formation": "line", "spacing": 1.33, "x": 0.0, "count": 0.93},),
    "catamaran": ({"formation": "line", "spacing": 1.17, "x": 0.0, "count": 1.66},),
    "condor": ({"x": 0.0, "count": 0.35},),
    "dart": (
        {"formation": "column", "interval": 0.4, "x": -0.5, "count": 4.0},
        {"formation": "column", "interval": 0.4, "x": 0.58, "count": 3.73},
        {"formation": "column", "interval": 0.35, "x": -0.5, "count": 3.54},
    ),
    "diver": (
        {"formation": "line", "spacing": 0.83, "count": 3.0},
        {"formation": "line", "spacing": 0.58, "count": 2.63},
        {"formation": "line", "spacing": 0.5, "count": 3.87},
    ),
    "drone": (
        {"formation": "column", "x": -0.67, "count": 5.0},
        {"formation": "column", "x": 0.67, "count": 5.0},
        {"formation": "line", "count": 5.04},
        {"formation": "line", "spacing": 0.5, "count": 4.0},
        {"formation": "column", "interval": 0.45, "x": -0.67, "count": 3.39},
        {"formation": "column", "interval": 0.45, "x": 0.67, "count": 3.39},
        {"formation": "line", "spacing": 0.33, "count": 4.27},
        {"formation": "column", "x": 0.0, "count": 3.04},
    ),
    "flak_cannon": (
        {"formation": "line", "spacing": 1.17, "x": 0.0, "count": 1.29},
        {"formation": "line", "spacing": 1.32, "x": 0.0, "count": 0.89},
        {"formation": "line", "spacing": 1.1, "x": 0.0, "count": 1.47},
        {"formation": "line", "spacing": 1.42, "x": 0.0, "count": 1.0},
        {"formation": "line", "spacing": 1.37, "x": 0.0, "count": 1.32},
        {"formation": "line", "spacing": 1.15, "x": 0.0, "count": 1.28},
        {"formation": "line", "spacing": 1.33, "x": 0.0, "count": 0.88},
        {"formation": "line", "spacing": 1.22, "x": 0.0, "count": 0.77},
        {"formation": "line", "spacing": 1.05, "x": 0.0, "count": 0.78},
        {"formation": "line", "spacing": 1.2, "x": 0.0, "count": 0.79},
        {"formation": "line", "spacing": 1.48, "x": 0.0, "count": 0.76},
        {"formation": "line", "spacing": 1.08, "x": 0.0, "count": 0.64},
        {"formation": "line", "spacing": 1.18, "x": 0.0, "count": 0.62},
        {"formation": "line", "spacing": 1.28, "x": 0.0, "count": 0.6},
        {"formation": "line", "spacing": 1.25, "x": 0.0, "count": 0.56},
    ),
    "freighter": (
        {"x": -0.5, "count": 0.66},
        {"x": 0.5, "count": 0.6},
    ),
    "gunship": (
        {"formation": "column", "x": 0.0, "count": 0.85},
        {"formation": "line", "spacing": 1.33, "count": 0.85},
    ),
    "harrier": (
        {"x": 0.0, "count": 0.54},
        {"x": -0.33, "count": 0.45},
        {"formation": "line", "spacing": 1.5, "x": 0.0, "count": 0.62},
    ),
    "hornet": (
        {"formation": "column", "interval": 0.9, "x": -0.33, "count": 2.71},
        {"formation": "column", "interval": 0.9, "x": 0.5, "count": 2.44},
        {"formation": "column", "interval": 0.9, "x": 0.0, "count": 1.92},
    ),
    "howitzer": (
        {"x": 0.5, "count": 0.49},
        {"x": -0.5, "count": 0.38},
    ),
    "hunter": (
        {"formation": "column", "x": -0.45, "count": 0.76},
        {"formation": "column", "x": 0.33, "count": 0.71},
        {"formation": "column", "x": 0.3, "count": 0.66},
        {"formation": "column", "x": 0.02, "count": 0.64},
        {"formation": "column", "x": -0.4, "count": 0.41},
        {"formation": "column", "x": -0.18, "count": 0.45},
        {"formation": "column", "x": -0.07, "count": 0.44},
        {"formation": "column", "x": -0.58, "count": 0.37},
        {"formation": "column", "x": 0.15, "count": 0.33},
        {"formation": "column", "x": 0.28, "count": 0.32},
        {"formation": "column", "x": 0.35, "count": 0.3},
        {"formation": "column", "x": -0.15, "count": 0.29},
    ),
    "imp": (
        {"formation": "line", "spacing": 0.75, "x": 0.0, "count": 2.67},
        {"formation": "line", "spacing": 0.67, "x": 0.0, "count": 2.15},
    ),
    "javelin": (
        {"formation": "column", "interval": 1.5, "x": 0.5, "count": 0.98},
        {"formation": "column", "interval": 1.5, "x": -0.5, "count": 0.94},
    ),
    "kestrel": (
        {"formation": "column", "interval": 1.2, "side": "left", "y": 0.6, "count": 1.28},
        {"formation": "column", "interval": 1.2, "side": "right", "y": 0.55, "count": 1.32},
    ),
    "lancer": (
        {"formation": "column", "x": -0.15, "count": 0.58},
        {"formation": "column", "x": 0.58, "count": 0.52},
        {"formation": "column", "x": -0.7, "count": 0.5},
        {"formation": "column", "x": -0.63, "count": 0.45},
        {"formation": "column", "x": 0.08, "count": 0.44},
        {"formation": "column", "x": 0.07, "count": 0.4},
        {"formation": "column", "x": -0.47, "count": 0.34},
        {"formation": "column", "x": -0.55, "count": 0.3},
    ),
    "manta": (
        {"formation": "column", "interval": 1.2, "side": "left", "y": 0.5, "count": 0.46},
        {"formation": "column", "interval": 1.2, "side": "right", "y": 0.5, "count": 0.49},
    ),
    "mine_layer": (
        {"formation": "column", "side": "left", "y": 0.6, "count": 0.54},
        {"formation": "column", "side": "right", "y": 0.4, "count": 0.46},
        {"formation": "column", "side": "left", "y": 0.7, "count": 0.54},
        {"formation": "column", "side": "right", "y": 0.3, "count": 0.51},
        {"formation": "column", "side": "left", "y": 0.5, "count": 0.47},
        {"formation": "column", "side": "right", "y": 0.5, "count": 0.42},
        {"formation": "column", "side": "left", "y": 0.3, "count": 0.4},
        {"formation": "column", "side": "right", "y": 0.6, "count": 0.39},
        {"formation": "column", "side": "left", "y": 0.4, "count": 0.34},
        {"formation": "column", "side": "right", "y": 0.7, "count": 0.36},
    ),
    "missile_silo": (
        {"formation": "column", "x": 0.12, "count": 0.73},
        {"formation": "column", "x": 0.08, "count": 0.66},
        {"formation": "column", "x": 0.22, "count": 0.62},
        {"formation": "column", "x": -0.6, "count": 0.38},
        {"formation": "column", "x": 0.07, "count": 0.36},
        {"formation": "column", "x": 0.6, "count": 0.31},
    ),
    "mite": (
        {"formation": "line", "spacing": 0.75, "x": 0.0, "count": 2.85},
        {"formation": "line", "spacing": 0.67, "x": 0.0, "count": 1.75},
    ),
    "needle": (
        {"x": 0.0, "count": 0.68},
        {"x": 0.33, "count": 0.47},
    ),
    "outrider": ({"formation": "line", "spacing": 1.33, "x": 0.0, "count": 1.3},),
    "pincer": (
        {"x": 0.0, "count": 0.32},
        {"x": -0.33, "count": 0.28},
    ),
    "rampart": (
        {"x": 0.0, "count": 0.44},
        {"x": -0.33, "count": 0.37},
        {"x": 0.5, "count": 0.3},
    ),
    "rapier": (
        {"formation": "column", "interval": 1.0, "x": 0.5, "count": 1.47},
        {"formation": "column", "interval": 0.8, "x": -0.5, "count": 1.85},
        {"formation": "column", "interval": 0.8, "x": 0.5, "count": 0.96},
    ),
    "rocket_truck": (
        {"formation": "column", "interval": 1.2, "x": 0.0, "count": 0.99},
        {"formation": "column", "interval": 1.2, "x": 0.58, "count": 0.9},
        {"formation": "column", "interval": 1.2, "x": -0.58, "count": 0.93},
    ),
    "rocketeer": ({"formation": "line", "spacing": 1.17, "x": 0.0, "count": 1.11},),
    "scrapper": ({"formation": "line", "spacing": 0.83, "x": 0.0, "count": 1.64},),
    "serpent": (
        {"formation": "column", "interval": 0.8, "x": -0.43, "count": 2.71},
        {"formation": "column", "interval": 0.8, "x": 0.12, "count": 2.61},
        {"formation": "column", "interval": 0.8, "x": -0.58, "count": 2.36},
        {"formation": "column", "interval": 0.8, "x": 0.1, "count": 2.28},
        {"formation": "column", "interval": 0.8, "x": -0.72, "count": 1.92},
        {"formation": "column", "interval": 0.8, "x": 0.0, "count": 1.73},
        {"formation": "column", "interval": 0.8, "x": 0.7, "count": 1.51},
        {"formation": "column", "interval": 0.8, "x": -0.23, "count": 1.46},
        {"formation": "column", "interval": 0.8, "x": -0.75, "count": 1.41},
        {"formation": "column", "interval": 0.8, "x": -0.25, "count": 1.23},
        {"formation": "column", "interval": 0.8, "x": -0.45, "count": 1.19},
        {"formation": "column", "interval": 0.8, "x": 0.67, "count": 1.03},
        {"formation": "column", "interval": 0.8, "x": -0.28, "count": 0.96},
        {"formation": "column", "interval": 0.8, "x": -0.38, "count": 0.87},
        {"formation": "column", "interval": 0.8, "x": 0.57, "count": 0.84},
        {"formation": "column", "interval": 0.8, "x": 0.48, "count": 0.81},
        {"formation": "column", "interval": 0.8, "x": -0.6, "count": 0.78},
    ),
    "shield_carrier": (
        {"formation": "column", "x": 0.0, "count": 0.79},
        {"formation": "line", "spacing": 1.33, "count": 0.84},
    ),
    "sniper": (
        {"formation": "line", "spacing": 1.67, "count": 0.93},
        {"formation": "column", "x": 0.0, "count": 0.77},
    ),
    "spark": (
        {"formation": "column", "interval": 0.3, "x": 0.67, "count": 4.83},
        {"formation": "column", "interval": 0.3, "x": -0.67, "count": 4.21},
        {"formation": "column", "interval": 0.3, "x": 0.0, "count": 2.37},
    ),
    "splitter": (
        {"formation": "line", "spacing": 1.33, "count": 1.57},
        {"formation": "column", "interval": 1.5, "x": 0.0, "count": 2.36},
        {"formation": "line", "spacing": 0.83, "count": 1.6},
    ),
    "stalker": (
        {"formation": "line", "spacing": 1.33, "x": 0.0, "count": 1.4},
        {"formation": "line", "spacing": 0.83, "x": 0.0, "count": 1.07},
    ),
    "stormcrow": (
        {"x": 0.0, "count": 0.33},
        {"x": -0.33, "count": 0.3},
        {"x": 0.33, "count": 0.26},
    ),
    "swarmer": (
        {"formation": "column", "interval": 0.2, "side": "left", "y": 0.4, "count": 4.78},
        {"formation": "column", "interval": 0.2, "side": "right", "y": 0.4, "count": 4.78},
        {"formation": "column", "interval": 0.2, "side": "left", "y": 0.6, "count": 5.09},
        {"formation": "column", "interval": 0.2, "side": "right", "y": 0.6, "count": 5.09},
        {"formation": "column", "interval": 0.2, "side": "left", "y": 0.3, "count": 5.34},
        {"formation": "column", "interval": 0.2, "side": "right", "y": 0.3, "count": 5.34},
        {"formation": "column", "interval": 0.2, "side": "left", "y": 0.5, "count": 5.16},
        {"formation": "column", "interval": 0.2, "side": "right", "y": 0.5, "count": 5.16},
    ),
    "tank": (
        {"formation": "column", "interval": 3.0, "x": -0.75, "count": 0.53},
        {"formation": "column", "interval": 3.0, "x": 0.75, "count": 0.7},
    ),
    "tick": (
        {"formation": "line", "spacing": 0.83, "x": 0.0, "count": 2.71},
        {"formation": "line", "spacing": 0.67, "x": 0.0, "count": 2.01},
    ),
    "turret": (
        {"formation": "line", "spacing": 1.67, "count": 1.42},
        {"formation": "line", "spacing": 1.0, "count": 1.13},
        {"formation": "line", "spacing": 0.83, "count": 1.11},
    ),
    "warhawk": (
        {"x": 0.0, "count": 0.34},
        {"x": 0.33, "count": 0.34},
    ),
    "weaver": (
        {"formation": "column", "interval": 0.4, "x": 0.0, "count": 5.09},
        {"formation": "column", "interval": 0.4, "x": -0.58, "count": 4.25},
        {"formation": "column", "interval": 0.4, "x": 0.58, "count": 4.25},
        {"formation": "column", "interval": 0.35, "x": 0.0, "count": 8.0},
        {"formation": "column", "interval": 0.38, "x": -0.67, "count": 5.14},
        {"formation": "column", "interval": 0.38, "x": 0.67, "count": 4.97},
        {"formation": "column", "interval": 0.38, "x": 0.0, "count": 4.81},
        {"formation": "column", "interval": 0.4, "x": -0.67, "count": 3.8},
        {"formation": "column", "interval": 0.4, "x": 0.67, "count": 3.8},
    ),
    "wisp": (
        {"formation": "line", "spacing": 1.33, "x": 0.0, "count": 1.37},
        {"formation": "line", "spacing": 0.83, "x": 0.0, "count": 1.32},
    ),
}


@dataclass(frozen=True)
class LevelPlan:
    name: str
    boss: str
    time_of_day: str = "day"
    clouds: float = 0.0
    seed: int = 0  # the background's layout (0: one of its own)
    scenery: dict[str, Any] = field(default_factory=dict)  # changes to the world's preset


@dataclass(frozen=True)
class WorldPlan:
    name: str
    background: str  # its ground: a preset of levels/sceneries.json
    levels: tuple[LevelPlan, ...]
    ground_units: bool = True  # False over water: no tanks or turrets


WORLDS = (
    WorldPlan(
        "Highlands",
        "mountains",
        (
            LevelPlan("High Peaks", "sentinel", clouds=0.6, seed=2828),
            LevelPlan(
                "Pine Ridge",
                "thresher",
                clouds=0.15,
                scenery={"ground": {"shape": {"range_size": 1.4, "crest_size": 0.5}}},
            ),
            LevelPlan(
                "Glacier Pass",
                "prowler",
                clouds=0.4,
                scenery={"haze": {"amount": 0.55}, "ground": {"colors": {"snow": [0.46, 0.48, 0.53]}}},
            ),
            LevelPlan("Stormcrest", "pulsar", clouds=0.85, scenery={"ground": {"shape": {"crest_size": 0.75}}}),
            LevelPlan("Dusk Peaks", "rockbreaker", "dusk", 0.3, scenery={"ground": {"shape": {"range_size": 0.9}}}),
            LevelPlan(
                "Summit", "warden", "night", 0.5, scenery={"ground": {"shape": {"range_size": 1.2, "crest_size": 0.7}}}
            ),
        ),
    ),
    WorldPlan(
        "Wildwood",
        "forest",
        (
            LevelPlan("Greenwood", "patrol_drone", clouds=0.5, seed=1111),
            LevelPlan(
                "Riverbend",
                "cyclone",
                clouds=0.2,
                scenery={"ground": {"shape": {"river_spacing": 1.8, "river_width": 0.16}}},
            ),
            LevelPlan(
                "Deep Canopy",
                "siege_pod",
                clouds=0.35,
                scenery={"ground": {"shape": {"canopy_size": 1.1, "river_spacing": 4.0}}},
            ),
            LevelPlan(
                "Autumn Wood",
                "delta_raider",
                clouds=0.3,
                scenery={
                    "ground": {
                        "colors": {
                            "tree_a": [0.16, 0.1, 0.04],
                            "tree_b": [0.09, 0.05, 0.03],
                            "tree_c": [0.14, 0.13, 0.05],
                        }
                    }
                },
            ),
            LevelPlan("Twilight Grove", "breacher", "dusk", 0.8, scenery={"ground": {"shape": {"canopy_size": 0.7}}}),
            LevelPlan("Moonlit Woods", "harvester", "night", 0.25),
        ),
    ),
    WorldPlan(
        "Fenlands",
        "swamp",
        (
            LevelPlan("Mire", "turbine", clouds=0.6, seed=1212),
            LevelPlan("Reedwater", "clamp_barge", clouds=0.15, scenery={"ground": {"shape": {"water_share": 0.55}}}),
            LevelPlan("Mistmarsh", "spire", clouds=0.8, scenery={"haze": {"amount": 0.6}}),
            LevelPlan(
                "Sunken Bog",
                "twin_fang",
                "dusk",
                0.4,
                scenery={"ground": {"shape": {"water_share": 0.35, "size": 0.55}}},
            ),
            LevelPlan(
                "Witchlight", "frigate", "night", 0.5, scenery={"fluid": {"colors": {"deep": [0.02, 0.08, 0.06]}}}
            ),
            LevelPlan("Fogbound Fen", "tidebreaker", "night", 0.85),
        ),
        ground_units=False,
    ),
    WorldPlan(
        "Heartland",
        "farmland",
        (
            LevelPlan("Harvest Dusk", "picket", "dusk", 0.1, seed=1313),
            LevelPlan(
                "Golden Fields",
                "bulwark",
                clouds=0.15,
                scenery={"settlement": {"layout": {"fields": ["wheat", "wheat", "wheat", "crop", "plowed", "wheat"]}}},
            ),
            LevelPlan(
                "Lavender Rows",
                "borer",
                clouds=0.25,
                scenery={
                    "settlement": {
                        "layout": {"fields": ["lavender", "lavender", "crop", "wheat", "plowed", "lavender"]}
                    }
                },
            ),
            LevelPlan(
                "Orchard Country",
                "silo_hauler",
                clouds=0.3,
                scenery={"settlement": {"layout": {"orchard_share": 0.3, "hedge_share": 0.6}}},
            ),
            LevelPlan("Hay Moon", "bastion", "night", 0.85, scenery={"settlement": {"layout": {"farm_share": 0.2}}}),
            LevelPlan(
                "Last Harvest",
                "reaper",
                "dusk",
                0.4,
                scenery={"settlement": {"layout": {"greenhouse_share": 0.15, "block": 0.4}}},
            ),
        ),
    ),
    WorldPlan(
        "Archipelago",
        "ocean",
        (
            LevelPlan("Archipelago", "enforcer", clouds=0.5, seed=1717),
            LevelPlan("Coral Shoals", "hive_carrier", clouds=0.15, scenery={"ground": {"shape": {"land_share": 0.15}}}),
            LevelPlan("Sunset Isles", "hover_tank", "dusk", 0.35),
            LevelPlan(
                "Open Sea", "cryo_fortress", clouds=0.6, scenery={"ground": {"shape": {"land_share": 0.1, "size": 0.9}}}
            ),
            LevelPlan("Squall Line", "sentry_grid", "dusk", 0.85, scenery={"ground": {"shape": {"land_share": 0.3}}}),
            LevelPlan("Dark Tide", "leviathan", "night", 0.4),
        ),
        ground_units=False,
    ),
    WorldPlan(
        "Canyonlands",
        "canyon",
        (
            LevelPlan("Red Canyon", "relay_array", clouds=0.15, seed=2626),
            LevelPlan(
                "Sandstone Gorge", "scavenger", clouds=0.1, scenery={"ground": {"shape": {"wall": 0.55, "steps": 5}}}
            ),
            LevelPlan(
                "Dry Riverbed", "mine_carrier", clouds=0.3, scenery={"ground": {"shape": {"river": 0.06, "floor": 0.3}}}
            ),
            LevelPlan("Canyon Dusk", "foundry", "dusk", 0.25),
            LevelPlan(
                "Switchbacks", "gunship_prime", "dusk", 0.8, scenery={"ground": {"shape": {"bend_spacing": 2.0}}}
            ),
            LevelPlan(
                "The Narrows", "colossus", "night", 0.2, scenery={"ground": {"shape": {"floor": 0.15, "wall": 0.35}}}
            ),
        ),
    ),
    WorldPlan(
        "Ironworks",
        "refinery",
        (
            LevelPlan("Refinery", "grappler", clouds=0.4, seed=3434),
            LevelPlan(
                "Tank Farm",
                "tugmaster",
                clouds=0.2,
                scenery={"settlement": {"layout": {"units": ["tanks", "tanks", "tanks", "pipes", "stack", "tanks"]}}},
            ),
            LevelPlan("Smelter", "magma_rig", "dusk", 0.5),
            LevelPlan(
                "Pipe Maze",
                "dreadnought",
                "dusk",
                0.3,
                scenery={"settlement": {"layout": {"units": ["pipes", "pipes", "plant", "stack", "tanks", "pipes"]}}},
            ),
            LevelPlan(
                "Flare Stacks",
                "flare_rig",
                "night",
                0.6,
                scenery={"settlement": {"layout": {"units": ["stack", "stack", "plant", "tanks", "cooling", "stack"]}}},
            ),
            LevelPlan(
                "Meltdown",
                "crucible",
                "night",
                0.8,
                scenery={
                    "settlement": {"layout": {"units": ["plant", "plant", "cooling", "stack", "tanks", "cooling"]}}
                },
            ),
        ),
    ),
    WorldPlan(
        "Metropolis",
        "city",
        (
            LevelPlan("Neon City", "executor", clouds=0.2, seed=3333),
            LevelPlan("Downtown", "interdictor", clouds=0.1, scenery={"settlement": {"layout": {"tower_share": 0.15}}}),
            LevelPlan(
                "Skyline",
                "nightwatch",
                "dusk",
                0.3,
                scenery={"settlement": {"layout": {"tower_share": 0.2, "midrise_share": 0.35}}},
            ),
            LevelPlan("Neon Rain", "arc_tower", "night", 0.7),
            LevelPlan(
                "Night Grid",
                "apex",
                "night",
                0.4,
                scenery={"settlement": {"layout": {"block": 0.3, "park_share": 0.03}}},
            ),
            LevelPlan("The Core", "overmind", "night", 0.9, scenery={"settlement": {"layout": {"tower_share": 0.25}}}),
        ),
    ),
)


def difficulty(world: int, level: int) -> int:
    """Level `level` of world `world` (both from 1)."""
    return 2 * (world - 1) + level


def _between(low_high: tuple[float, float], d: int) -> float:
    low, high = low_high
    return low + (high - low) * (d - 1) / (MAX_DIFFICULTY - 1)


def make_wave(rng: random.Random, enemy: str, d: int) -> dict[str, Any]:
    """A group of `enemy` (without its time), its shape drawn from the enemy's, its size grown to difficulty `d`."""
    shape = dict(rng.choice(SHAPES[enemy]))
    count = max(1, round(shape.pop("count") * GROWTH ** (d - 1)))
    if shape.get("formation") == "line" and count > 1:
        span = SIDE_SPAN if "side" in shape else LINE_SPAN
        count = min(count, int(span / shape.get("spacing", 0.2)) + 1)
    wave: dict[str, Any] = {"enemy": enemy}
    if count > 1 or "formation" in shape:
        wave["count"] = count
    return {**wave, **shape}


def threat(wave: dict[str, Any]) -> int:
    """What a wave is worth: the points of its enemies (the tougher an enemy, the more points)."""
    return wave.get("count", 1) * ENEMY_TYPES[wave["enemy"]].points


def make_level(rng: random.Random, world: WorldPlan, plan: LevelPlan, d: int) -> dict[str, Any]:
    pool = sorted(
        enemy for enemy, unlock in UNLOCK.items() if unlock <= d and (world.ground_units or enemy not in GROUND)
    )
    newest = [enemy for enemy in pool if UNLOCK[enemy] == d]
    older = [enemy for enemy in pool if enemy not in newest]
    signature = (newest + rng.sample(older, len(older)))[: rng.randint(2, 3)]
    weights = [1 + UNLOCK[enemy] for enemy in pool]  # the newer enemies more often
    main = list(signature)
    while len(main) < min(round(_between(KINDS, d)), len(pool)):
        enemy = rng.choices(pool, weights)[0]
        if enemy not in main:
            main.append(enemy)
    # The waves, until their threat reaches the level's; the last ones (the finale) of the signature enemies.
    budget = THREAT[0] + (THREAT[1] - THREAT[0]) * ((d - 1) / (MAX_DIFFICULTY - 1)) ** THREAT_CURVE
    groups = [make_wave(rng, rng.choice([e for e in WARM_UP if e in pool]), d)]
    while sum(map(threat, groups)) < budget:
        finale = sum(map(threat, groups)) > budget * (1 - FINALE_SHARE)
        groups.append(make_wave(rng, rng.choice(signature if finale else main), d))
    # Spread over the level: each wave gets time in proportion to its threat; sometimes two come together.
    total = sum(map(threat, groups))
    finale_from = next(
        i for i, _ in enumerate(groups) if sum(map(threat, groups[: i + 1])) > total * (1 - FINALE_SHARE)
    )
    twins = _between(TWIN_WAVES, d)
    time, waves = 2.0, []
    for i, group in enumerate(groups):
        if i > 0 and not (rng.random() < twins and waves[-1]["time"] == time):
            share = LEVEL_TIME * threat(groups[i - 1]) / total
            time += max(MIN_GAP, share * (FINALE_PACE if i > finale_from else rng.uniform(0.8, 1.2)))
        waves.append({"time": time, **group})
    stretch = (LEVEL_TIME - 2.0) / max(time - 2.0, 1.0)  # the last wave at LEVEL_TIME
    for wave in waves:
        wave["time"] = round(2.0 + (wave["time"] - 2.0) * stretch, 1)
    waves.append({"time": round(LEVEL_TIME + BOSS_DELAY, 1), "enemy": plan.boss})
    level: dict[str, Any] = {
        "name": plan.name,
        "scroll_speed": round(_between(SCROLL_SPEED, d), 3),
        "background": world.background,
        "background_seed": plan.seed or rng.randint(100, 9999),
    }
    if plan.time_of_day != "day":
        level["time_of_day"] = plan.time_of_day
    if plan.clouds:
        level["clouds"] = plan.clouds
    if plan.scenery:
        level["scenery"] = plan.scenery
    return {**level, "waves": waves}


def generate(seed: int) -> dict[tuple[int, int], dict[str, Any]]:
    """Every level, by (world, level) from 1."""
    rng = random.Random(seed)  # noqa: S311 - level layouts, not cryptography
    return {
        (w, n): make_level(rng, world, plan, difficulty(w, n))
        for w, world in enumerate(WORLDS, start=1)
        for n, plan in enumerate(world.levels, start=1)
    }


def write(folder: Path, levels: dict[tuple[int, int], dict[str, Any]]) -> None:
    """Replace every world folder with the generated ones (the background presets, sceneries.json, stay)."""
    for old in folder.glob("world_*"):
        for path in old.glob("*.json"):
            path.unlink()
        old.rmdir()
    for w, world in enumerate(WORLDS, start=1):
        world_folder = folder / f"world_{w}"
        world_folder.mkdir()
        (world_folder / "world.json").write_text(json.dumps({"name": world.name}, indent=2) + "\n")
    for (w, n), level in levels.items():
        (folder / f"world_{w}" / f"level_{n}.json").write_text(json.dumps(level, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"the waves' draw (default {DEFAULT_SEED})")
    parser.add_argument("--out", type=Path, default=LEVELS, help="where (default: the game's levels)")
    args = parser.parse_args()
    write(args.out, generate(args.seed))
    print(f"{sum(len(world.levels) for world in WORLDS)} levels in {len(WORLDS)} worlds written to {args.out}")


if __name__ == "__main__":
    main()
