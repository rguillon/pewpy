"""The Rust Pan world: candidate #010 of the background candidates (copper_pan), its levels varying it."""

from pewpy.tools.levels.plan import LevelPlan, WorldPlan

RUST_PAN = WorldPlan(
    "Rust Pan",
    "salt_pan",
    (
        LevelPlan("Rust Pan", "enforcer", "maelstrom", "dusk", seed=791353),
        LevelPlan(
            "Copper Flats", "hive_carrier", "man_o_war", clouds=0.15, scenery={"ground": {"shape": {"pool_share": 0.1}}}
        ),
        LevelPlan(
            "Brine Pools", "hover_tank", "typhoon", clouds=0.35, scenery={"ground": {"shape": {"pool_share": 0.28}}}
        ),
        LevelPlan("Mineral Dusk", "cryo_fortress", "tsunami", "dusk", 0.3),
        LevelPlan("Dust Storm", "sentry_grid", "abyssal", "dusk", 0.85, scenery={"haze": {"amount": 0.7}}),
        LevelPlan("Night Crust", "leviathan", "kraken", "night", 0.4),
    ),
    ground_units=False,  # no tanks: the waves the world in its place had (over water) *(placeholder)*
    scenery={
        "ground": {
            "shape": {"size": 0.69, "pool_share": 0.176},
            "colors": {
                "crust_a": [0.262, 0.144, 0.085],
                "crust_b": [0.322, 0.178, 0.104],
                "ridge": [0.32, 0.231, 0.134],
                "crack": [0.078, 0.052, 0.031],
                "shore": [0.137, 0.128, 0.095],
            },
        },
        "fluid": {
            "kind": "water",
            "colors": {"deep": [0.021, 0.085, 0.081], "shallow": [0.056, 0.221, 0.188], "foam": [0.303, 0.327, 0.369]},
        },
        "haze": {"color": [0.359, 0.271, 0.209], "amount": 0.544},
    },
)
