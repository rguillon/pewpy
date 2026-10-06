"""The Highlands world."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

HIGHLANDS = WorldPlan(
    "Highlands",
    "mountains",
    (
        LevelPlan("High Peaks", "sentinel", "avalanche", clouds=0.1, seed=2828),
        LevelPlan(
            "Pine Ridge",
            "thresher",
            "frostjaw",
            time_of_day="night",
            clouds=0.5,
            scenery={"ground": {"shape": {"range_size": 1.4, "crest_size": 0.5}}},
        ),
        LevelPlan(
            "Glacier Pass",
            "prowler",
            "iron_summit",
            clouds=0.45,
            scenery={"haze": {"amount": 0.55}, "ground": {"colors": {"snow": [0.46, 0.48, 0.53]}}},
        ),
        LevelPlan(
            "Stormcrest",
            "pulsar",
            "stormpeak",
            time_of_day="dusk",
            clouds=0.9,
            scenery={"ground": {"shape": {"crest_size": 0.75}}},
        ),
        LevelPlan(
            "Dusk Peaks",
            "rockbreaker",
            "ridgebreaker",
            time_of_day="dusk",
            clouds=0.2,
            scenery={"ground": {"shape": {"range_size": 0.9}}},
        ),
        LevelPlan(
            "Summit",
            "warden",
            "highlord",
            time_of_day="night",
            clouds=0.7,
            scenery={"ground": {"shape": {"range_size": 1.2, "crest_size": 0.7}}},
        ),
    ),
)
