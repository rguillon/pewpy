"""The Wildwood world."""

from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan

WILDWOOD = WorldPlan(
    "Wildwood",
    "forest",
    (
        LevelPlan("Greenwood", "patrol_drone", "ironbark", clouds=0.5, seed=1111),
        LevelPlan(
            "Riverbend",
            "cyclone",
            "thornback",
            clouds=0.2,
            scenery={"ground": {"shape": {"river_spacing": 1.8, "river_width": 0.16}}},
        ),
        LevelPlan(
            "Deep Canopy",
            "siege_pod",
            "rootmaw",
            clouds=0.35,
            scenery={"ground": {"shape": {"canopy_size": 1.1, "river_spacing": 4.0}}},
        ),
        LevelPlan(
            "Autumn Wood",
            "delta_raider",
            "wildfire",
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
        LevelPlan(
            "Twilight Grove",
            "breacher",
            "grovekeeper",
            "dusk",
            0.8,
            scenery={"ground": {"shape": {"canopy_size": 0.7}}},
        ),
        LevelPlan("Moonlit Woods", "harvester", "old_growth", "night", 0.25),
    ),
)
