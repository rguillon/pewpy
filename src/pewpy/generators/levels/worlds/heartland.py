"""The Heartland world."""

from pewpy.generators.levels.plan import LevelPlan, WorldPlan

HEARTLAND = WorldPlan(
    "Heartland",
    "farmland",
    (
        LevelPlan("Harvest Dusk", "picket", "scarecrow", time_of_day="dusk", clouds=0.1, seed=1313),
        LevelPlan(
            "Golden Fields",
            "bulwark",
            "combine",
            clouds=0.4,
            scenery={"settlement": {"layout": {"fields": ["wheat", "wheat", "wheat", "crop", "plowed", "wheat"]}}},
        ),
        LevelPlan(
            "Lavender Rows",
            "borer",
            "locust",
            time_of_day="night",
            clouds=0.6,
            scenery={
                "settlement": {"layout": {"fields": ["lavender", "lavender", "crop", "wheat", "plowed", "lavender"]}}
            },
        ),
        LevelPlan(
            "Orchard Country",
            "silo_hauler",
            "granary",
            clouds=0.2,
            scenery={"settlement": {"layout": {"orchard_share": 0.3, "hedge_share": 0.6}}},
        ),
        LevelPlan(
            "Hay Moon",
            "bastion",
            "harrowmaster",
            time_of_day="night",
            clouds=0.85,
            scenery={"settlement": {"layout": {"farm_share": 0.2}}},
        ),
        LevelPlan(
            "Last Harvest",
            "reaper",
            "black_harvest",
            time_of_day="dusk",
            clouds=0.5,
            scenery={"settlement": {"layout": {"greenhouse_share": 0.15, "block": 0.4}}},
        ),
    ),
)
