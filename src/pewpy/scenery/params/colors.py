"""The colors each painter and settlement needs, by name, in the order the ground shader reads them."""

# The colors each of the ground shader's painters uses (ground.colors), in the order it reads them; built-up grounds
# ("city", "refinery", "farmland") paint the settlement's surfaces with its colors instead (settlement.colors).
STYLE_COLORS: dict[str, tuple[str, ...]] = {
    "mountains": ("rock_low", "rock_high", "scree", "meadow_low", "meadow_high", "pine", "snow"),
    "city": (),
    "refinery": (),
    "farmland": (),
    "forest": ("tree_a", "tree_b", "tree_c", "clearing_low", "clearing_high"),
    "canyon": ("band_1", "band_2", "band_3", "band_4", "plateau", "sand", "green"),
    "salt_pan": ("crust_a", "crust_b", "ridge", "crack", "shore"),
    "savanna": ("grass_dry", "grass_gold", "grass_green", "sand", "rock"),
}
# The colors of what covers a settlement's ground (settlement.py Surface); "natural" is the ground between (park
# grass, scrub, grass), "lamp" the street lights at night.
SURFACE_COLORS: dict[str, tuple[str, ...]] = {
    "city": ("street", "lamp", "pavement", "natural_low", "natural_high"),
    "refinery": ("street", "lamp", "yard", "natural_low", "natural_high"),
    "farmland": (
        "dirt_road",
        "wheat",
        "crop",
        "plowed",
        "lavender",
        "pasture_low",
        "pasture_high",
        "farmyard",
        "natural_low",
        "natural_high",
    ),
}
# A fluid's colors, in the order the shader reads them.
FLUID_COLORS: dict[str, tuple[str, ...]] = {
    "water": ("deep", "shallow", "foam"),
}
