"""The Metropolis world."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

METROPOLIS = WorldPlan(
    "Metropolis",
    "city",
    (
        LevelPlan("Neon City", "executor", "neon_tyrant", time_of_day="dusk", clouds=0.2, seed=3333),
        LevelPlan(
            "Downtown", "interdictor", "gridlock", clouds=0.1, scenery={"settlement": {"layout": {"tower_share": 0.15}}}
        ),
        LevelPlan(
            "Skyline",
            "nightwatch",
            "blackout",
            clouds=0.5,
            scenery={"settlement": {"layout": {"tower_share": 0.2, "midrise_share": 0.35}}},
        ),
        LevelPlan("Neon Rain", "arc_tower", "skybreaker", time_of_day="night", clouds=0.9),
        LevelPlan(
            "Night Grid",
            "apex",
            "sovereign",
            time_of_day="night",
            clouds=0.35,
            scenery={"settlement": {"layout": {"block": 0.3, "park_share": 0.03}}},
        ),
        LevelPlan(
            "The Core",
            "overmind",
            "singularity",
            time_of_day="dusk",
            clouds=0.7,
            scenery={"settlement": {"layout": {"tower_share": 0.25}}},
        ),
    ),
)
