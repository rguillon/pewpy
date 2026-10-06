"""The Lush Veld world: candidate #001 of the background candidates (green_season), its levels varying it."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

LUSH_VELD = WorldPlan(
    "Lush Veld",
    "savanna",
    (
        LevelPlan("Lush Veld", "turbine", "bogmaw", time_of_day="dusk", clouds=0.21, seed=114383),
        LevelPlan(
            "Winding Sands",
            "clamp_barge",
            "mirelord",
            clouds=0.05,
            scenery={"ground": {"shape": {"bend_spacing": 0.9}}},
        ),
        LevelPlan(
            "Kopje Country",
            "spire",
            "fenwraith",
            time_of_day="night",
            clouds=0.5,
            scenery={"ground": {"shape": {"outcrop_share": 0.05}}},
        ),
        LevelPlan(
            "Acacia Dusk",
            "twin_fang",
            "hydra",
            time_of_day="dusk",
            clouds=0.4,
            scenery={"flora": {"knobs": {"chance": 0.028}}},
        ),
        LevelPlan("Long Grass", "frigate", "marsh_titan", clouds=0.85, scenery={"ground": {"shape": {"size": 1.5}}}),
        LevelPlan("Veld by Night", "tidebreaker", "drowned_king", time_of_day="night", clouds=0.3),
    ),
    ground_units=False,  # no tanks: the waves the world in its place had (over water) *(placeholder)*
    scenery={
        "ground": {
            "shape": {"size": 1.138, "bend_spacing": 1.261, "outcrop_share": 0.025},
            "colors": {
                "grass_dry": [0.137, 0.16, 0.074],
                "grass_gold": [0.179, 0.182, 0.083],
                "grass_green": [0.092, 0.155, 0.056],
                "sand": [0.291, 0.282, 0.218],
                "rock": [0.166, 0.165, 0.15],
            },
        },
        "flora": {"knobs": {"chance": 0.018}},
        "haze": {"color": [0.345, 0.335, 0.306], "amount": 0.364},
    },
)
