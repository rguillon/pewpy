"""The Bright Ridges world: candidate #022 of the background candidates (rainbow_hills), its levels varying it."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

BRIGHT_RIDGES = WorldPlan(
    "Bright Ridges",
    "badlands",
    (
        LevelPlan("Bright Ridges", "relay_array", "mesa", clouds=0.3, seed=243193),
        LevelPlan(
            "Striped Gullies",
            "scavenger",
            "dust_devil",
            time_of_day="night",
            clouds=0.1,
            scenery={"ground": {"shape": {"size": 0.6}}},
        ),
        LevelPlan(
            "Ochre Walls",
            "mine_carrier",
            "landslide",
            time_of_day="dusk",
            clouds=0.6,
            scenery={"ground": {"shape": {"floor": 0.2}}},
        ),
        LevelPlan("Red Dusk", "foundry", "basilisk", time_of_day="dusk", clouds=0.2),
        LevelPlan(
            "Rainbow Breaks", "gunship_prime", "sandworm", clouds=0.85, scenery={"ground": {"shape": {"size": 1.05}}}
        ),
        LevelPlan("Dark Strata", "colossus", "monolith", time_of_day="night", clouds=0.5),
    ),
    scenery={
        "ground": {
            "shape": {"size": 0.852, "floor": 0.282},
            "colors": {
                "band_1": [0.33, 0.122, 0.086],
                "band_2": [0.363, 0.208, 0.094],
                "band_3": [0.306, 0.281, 0.133],
                "band_4": [0.186, 0.214, 0.192],
                "plateau": [0.279, 0.2, 0.126],
                "sand": [0.281, 0.23, 0.147],
                "green": [0.116, 0.129, 0.07],
            },
        },
        "haze": {"color": [0.334, 0.271, 0.223], "amount": 0.515},
    },
)
