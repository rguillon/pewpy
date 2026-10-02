"""The Heartland world."""

from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan

HEARTLAND = WorldPlan(
    "Heartland",
    "farmland",
    (
        LevelPlan("Harvest Dusk", "picket", "scarecrow", "dusk", 0.1, seed=1313),
        LevelPlan(
            "Golden Fields",
            "bulwark",
            "combine",
            clouds=0.15,
            scenery={"settlement": {"layout": {"fields": ["wheat", "wheat", "wheat", "crop", "plowed", "wheat"]}}},
        ),
        LevelPlan(
            "Lavender Rows",
            "borer",
            "locust",
            clouds=0.25,
            scenery={
                "settlement": {"layout": {"fields": ["lavender", "lavender", "crop", "wheat", "plowed", "lavender"]}}
            },
        ),
        LevelPlan(
            "Orchard Country",
            "silo_hauler",
            "granary",
            clouds=0.3,
            scenery={"settlement": {"layout": {"orchard_share": 0.3, "hedge_share": 0.6}}},
        ),
        LevelPlan(
            "Hay Moon",
            "bastion",
            "harrowmaster",
            "night",
            0.85,
            scenery={"settlement": {"layout": {"farm_share": 0.2}}},
        ),
        LevelPlan(
            "Last Harvest",
            "reaper",
            "black_harvest",
            "dusk",
            0.4,
            scenery={"settlement": {"layout": {"greenhouse_share": 0.15, "block": 0.4}}},
        ),
    ),
)
