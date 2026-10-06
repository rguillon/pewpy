"""The Fenlands world."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

FENLANDS = WorldPlan(
    "Fenlands",
    "swamp",
    (
        LevelPlan("Mire", "turbine", "bogmaw", clouds=0.6, seed=1212),
        LevelPlan(
            "Reedwater",
            "clamp_barge",
            "mirelord",
            clouds=0.15,
            scenery={"ground": {"shape": {"water_share": 0.55}}},
        ),
        LevelPlan("Mistmarsh", "spire", "fenwraith", clouds=0.8, scenery={"haze": {"amount": 0.6}}),
        LevelPlan(
            "Sunken Bog",
            "twin_fang",
            "hydra",
            "dusk",
            0.4,
            scenery={"ground": {"shape": {"water_share": 0.35, "size": 0.9}}},
        ),
        LevelPlan(
            "Witchlight",
            "frigate",
            "marsh_titan",
            "night",
            0.5,
            scenery={"fluid": {"colors": {"deep": [0.02, 0.08, 0.06]}}},
        ),
        LevelPlan("Fogbound Fen", "tidebreaker", "drowned_king", "night", 0.85),
    ),
    ground_units=False,
)
