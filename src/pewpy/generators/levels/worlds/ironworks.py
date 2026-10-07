"""The Ironworks world."""

from pewpy.generators.levels.plan import LevelPlan, WorldPlan

IRONWORKS = WorldPlan(
    "Ironworks",
    "refinery",
    (
        LevelPlan("Refinery", "grappler", "furnace", clouds=0.4, seed=3434),
        LevelPlan(
            "Tank Farm",
            "tugmaster",
            "smokestack",
            time_of_day="night",
            clouds=0.15,
            scenery={"settlement": {"layout": {"units": ["tanks", "tanks", "tanks", "pipes", "stack", "tanks"]}}},
        ),
        LevelPlan("Smelter", "magma_rig", "slag_king", time_of_day="dusk", clouds=0.6),
        LevelPlan(
            "Pipe Maze",
            "dreadnought",
            "forgemaster",
            clouds=0.9,
            scenery={"settlement": {"layout": {"units": ["pipes", "pipes", "plant", "stack", "tanks", "pipes"]}}},
        ),
        LevelPlan(
            "Flare Stacks",
            "flare_rig",
            "inferno",
            time_of_day="night",
            clouds=0.3,
            scenery={"settlement": {"layout": {"units": ["stack", "stack", "plant", "tanks", "cooling", "stack"]}}},
        ),
        LevelPlan(
            "Meltdown",
            "crucible",
            "reactor",
            time_of_day="dusk",
            clouds=0.85,
            scenery={"settlement": {"layout": {"units": ["plant", "plant", "cooling", "stack", "tanks", "cooling"]}}},
        ),
    ),
)
