"""The Highlands world."""

from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan

HIGHLANDS = WorldPlan(
    "Highlands",
    "mountains",
    (
        LevelPlan("High Peaks", "sentinel", "avalanche", clouds=0.6, seed=2828),
        LevelPlan(
            "Pine Ridge",
            "thresher",
            "frostjaw",
            clouds=0.15,
            scenery={"ground": {"shape": {"range_size": 1.4, "crest_size": 0.5}}},
        ),
        LevelPlan(
            "Glacier Pass",
            "prowler",
            "iron_summit",
            clouds=0.4,
            scenery={"haze": {"amount": 0.55}, "ground": {"colors": {"snow": [0.46, 0.48, 0.53]}}},
        ),
        LevelPlan(
            "Stormcrest", "pulsar", "stormpeak", clouds=0.85, scenery={"ground": {"shape": {"crest_size": 0.75}}}
        ),
        LevelPlan(
            "Dusk Peaks",
            "rockbreaker",
            "ridgebreaker",
            "dusk",
            0.3,
            scenery={"ground": {"shape": {"range_size": 0.9}}},
        ),
        LevelPlan(
            "Summit",
            "warden",
            "highlord",
            "night",
            0.5,
            scenery={"ground": {"shape": {"range_size": 1.2, "crest_size": 0.7}}},
        ),
    ),
)
