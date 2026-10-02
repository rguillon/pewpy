"""The Steamvale world."""

from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan

STEAMVALE = WorldPlan(
    "Steamvale",
    "geysers",
    (
        LevelPlan("Geyser Basin", "relay_array", "mesa", clouds=0.15, seed=2626),
        LevelPlan(
            "Sinter Terraces",
            "scavenger",
            "dust_devil",
            clouds=0.1,
            scenery={"ground": {"shape": {"mound_spacing": 1.0, "steps": 5}}},
        ),
        LevelPlan(
            "Prismatic Springs",
            "mine_carrier",
            "landslide",
            clouds=0.3,
            scenery={"ground": {"shape": {"spring_radius": [0.06, 0.2], "mat_width": 2.0}}},
        ),
        LevelPlan("Sulfur Dusk", "foundry", "basilisk", "dusk", 0.25),
        LevelPlan(
            "Fumarole Field",
            "gunship_prime",
            "sandworm",
            "dusk",
            0.8,
            scenery={"ground": {"shape": {"spring_spacing": 0.3, "spring_radius": [0.04, 0.09]}}},
        ),
        LevelPlan(
            "The Caldera",
            "colossus",
            "monolith",
            "night",
            0.2,
            scenery={"ground": {"shape": {"ridge_share": 0.35}}},
        ),
    ),
)
