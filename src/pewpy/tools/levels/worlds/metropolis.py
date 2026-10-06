"""The Metropolis world."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

METROPOLIS = WorldPlan(
    "Metropolis",
    "city",
    (
        LevelPlan("Neon City", "executor", "neon_tyrant", clouds=0.2, seed=3333),
        LevelPlan(
            "Downtown",
            "interdictor",
            "gridlock",
            clouds=0.1,
            scenery={"settlement": {"layout": {"tower_share": 0.15}}},
        ),
        LevelPlan(
            "Skyline",
            "nightwatch",
            "blackout",
            "dusk",
            0.3,
            scenery={"settlement": {"layout": {"tower_share": 0.2, "midrise_share": 0.35}}},
        ),
        LevelPlan("Neon Rain", "arc_tower", "skybreaker", "night", 0.7),
        LevelPlan(
            "Night Grid",
            "apex",
            "sovereign",
            "night",
            0.4,
            scenery={"settlement": {"layout": {"block": 0.3, "park_share": 0.03}}},
        ),
        LevelPlan(
            "The Core",
            "overmind",
            "singularity",
            "night",
            0.9,
            scenery={"settlement": {"layout": {"tower_share": 0.25}}},
        ),
    ),
)
