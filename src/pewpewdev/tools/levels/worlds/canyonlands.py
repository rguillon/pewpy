"""The Canyonlands world."""

from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan

CANYONLANDS = WorldPlan(
    "Canyonlands",
    "canyon",
    (
        LevelPlan("Red Canyon", "relay_array", "mesa", clouds=0.15, seed=2626),
        LevelPlan(
            "Sandstone Gorge",
            "scavenger",
            "dust_devil",
            clouds=0.1,
            scenery={"ground": {"shape": {"wall": 0.55, "steps": 5}}},
        ),
        LevelPlan(
            "Dry Riverbed",
            "mine_carrier",
            "landslide",
            clouds=0.3,
            scenery={"ground": {"shape": {"river": 0.06, "floor": 0.3}}},
        ),
        LevelPlan("Canyon Dusk", "foundry", "basilisk", "dusk", 0.25),
        LevelPlan(
            "Switchbacks",
            "gunship_prime",
            "sandworm",
            "dusk",
            0.8,
            scenery={"ground": {"shape": {"bend_spacing": 2.0}}},
        ),
        LevelPlan(
            "The Narrows",
            "colossus",
            "monolith",
            "night",
            0.2,
            scenery={"ground": {"shape": {"floor": 0.15, "wall": 0.35}}},
        ),
    ),
)
