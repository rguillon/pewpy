"""The Ironworks world."""

from pewpewdev.tools.levels.plan import LevelPlan, WorldPlan

IRONWORKS = WorldPlan(
    "Ironworks",
    "refinery",
    (
        LevelPlan("Refinery", "grappler", "furnace", clouds=0.4, seed=3434),
        LevelPlan(
            "Tank Farm",
            "tugmaster",
            "smokestack",
            clouds=0.2,
            scenery={"settlement": {"layout": {"units": ["tanks", "tanks", "tanks", "pipes", "stack", "tanks"]}}},
        ),
        LevelPlan("Smelter", "magma_rig", "slag_king", "dusk", 0.5),
        LevelPlan(
            "Pipe Maze",
            "dreadnought",
            "forgemaster",
            "dusk",
            0.3,
            scenery={"settlement": {"layout": {"units": ["pipes", "pipes", "plant", "stack", "tanks", "pipes"]}}},
        ),
        LevelPlan(
            "Flare Stacks",
            "flare_rig",
            "inferno",
            "night",
            0.6,
            scenery={"settlement": {"layout": {"units": ["stack", "stack", "plant", "tanks", "cooling", "stack"]}}},
        ),
        LevelPlan(
            "Meltdown",
            "crucible",
            "reactor",
            "night",
            0.8,
            scenery={"settlement": {"layout": {"units": ["plant", "plant", "cooling", "stack", "tanks", "cooling"]}}},
        ),
    ),
)
