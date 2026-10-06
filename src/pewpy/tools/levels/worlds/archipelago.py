"""The Archipelago world."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

ARCHIPELAGO = WorldPlan(
    "Archipelago",
    "ocean",
    (
        LevelPlan("Archipelago", "enforcer", "maelstrom", clouds=0.5, seed=1717),
        LevelPlan(
            "Coral Shoals",
            "hive_carrier",
            "man_o_war",
            clouds=0.15,
            scenery={"ground": {"shape": {"land_share": 0.15}}},
        ),
        LevelPlan("Sunset Isles", "hover_tank", "typhoon", "dusk", 0.35),
        LevelPlan(
            "Open Sea",
            "cryo_fortress",
            "tsunami",
            clouds=0.6,
            scenery={"ground": {"shape": {"land_share": 0.1, "size": 0.9}}},
        ),
        LevelPlan(
            "Squall Line",
            "sentry_grid",
            "abyssal",
            "dusk",
            0.85,
            scenery={"ground": {"shape": {"land_share": 0.3}}},
        ),
        LevelPlan("Dark Tide", "leviathan", "kraken", "night", 0.4),
    ),
    ground_units=False,
)
