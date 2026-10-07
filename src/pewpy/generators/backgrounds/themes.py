"""The themes: each a way of showing one of the new kinds of ground (03-levels.md, "Backgrounds") as a background.

The new kinds: a salt pan, a savanna, badlands (their presets in levels/sceneries.json, their generators in
pewpy.scenery.ground.kinds, their painters in its shader). Earth-like only, after real places (no alien colors). A
theme starts from one of them and gives it its own palette (kept dark and muted, like the presets, so bullets stand
out), sometimes other water, its numbers (each within a range the generator draws well), its times of day and
clouds. Each candidate of a theme varies it a little more (`vary`), and gets a name from the theme's words.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pewpy.generators.models.common.geometry import Rng

Color = list[float]
Changes = dict[str, Any]


@dataclass(frozen=True)
class Theme:
    """A way of changing a preset: what it starts from, how it's named, when it's seen, and its changes."""

    preset: str
    adjectives: tuple[str, ...]
    nouns: tuple[str, ...]
    times: tuple[str, ...]  # its times of day, picked at random (a time listed twice comes twice as often)
    clouds: tuple[float, float]  # see-through clouds over the ground, between
    changes: Callable[[Rng], Changes]  # the scenery's changes (see pewpy.scenery.params)


def vary(rng: Rng, color: Color, spread: float = 0.08) -> Color:
    """Return a color a little different: each channel up to `spread` of itself brighter or darker."""
    return [round(min(1.0, channel * rng.uniform(1 - spread, 1 + spread)), 3) for channel in color]


def palette(rng: Rng, colors: dict[str, Color]) -> dict[str, Color]:
    """Return each color a little different (see `vary`)."""
    return {name: vary(rng, color) for name, color in colors.items()}


def between(rng: Rng, low: float, high: float) -> float:
    """Return a number between `low` and `high`, rounded."""
    return round(rng.uniform(low, high), 3)


def water(rng: Rng, deep: Color, shallow: Color, foam: Color = [0.3, 0.33, 0.36]) -> Changes:  # noqa: B006
    """Return a fluid of water."""
    return {"kind": "water", "colors": palette(rng, {"deep": deep, "shallow": shallow, "foam": foam})}


def haze(rng: Rng, color: Color, low: float = 0.35, high: float = 0.55) -> Changes:
    """Return a haze of `color`, its amount between `low` and `high`."""
    return {"color": vary(rng, color), "amount": between(rng, low, high)}


# The salt pans


def _pan(rng: Rng, pools: tuple[float, float]) -> Changes:
    return {"size": between(rng, 0.6, 1.0), "pool_share": between(rng, *pools)}


def salt_flat(rng: Rng) -> Changes:
    """White plates and pink brine."""
    return {"ground": {"shape": _pan(rng, (0.1, 0.2))}, "haze": haze(rng, [0.36, 0.34, 0.32])}


def turquoise_pan(rng: Rng) -> Changes:
    """Pale plates round turquoise pools."""
    return {"ground": {"shape": _pan(rng, (0.2, 0.3))},
            "fluid": water(rng, [0.02, 0.1, 0.12], [0.08, 0.28, 0.3]),
            "haze": haze(rng, [0.32, 0.36, 0.36])}  # fmt: skip


def copper_pan(rng: Rng) -> Changes:
    """Orange mineral crust, blue-green pools."""
    colors = {"crust_a": [0.26, 0.15, 0.08], "crust_b": [0.3, 0.19, 0.1], "ridge": [0.34, 0.24, 0.14],
              "crack": [0.08, 0.05, 0.03], "shore": [0.14, 0.12, 0.1]}  # fmt: skip
    return {"ground": {"shape": _pan(rng, (0.12, 0.25)), "colors": palette(rng, colors)},
            "fluid": water(rng, [0.02, 0.08, 0.08], [0.06, 0.22, 0.2]),
            "haze": haze(rng, [0.34, 0.26, 0.2])}  # fmt: skip


def clay_pan(rng: Rng) -> Changes:
    """Make a pale grey-green clay pan, cracked, a few muddy pools, like Etosha."""
    colors = {"crust_a": [0.22, 0.22, 0.19], "crust_b": [0.26, 0.26, 0.22], "ridge": [0.3, 0.3, 0.26],
              "crack": [0.1, 0.09, 0.08], "shore": [0.16, 0.14, 0.11]}  # fmt: skip
    return {"ground": {"shape": _pan(rng, (0.04, 0.08)), "colors": palette(rng, colors)},
            "fluid": water(rng, [0.08, 0.07, 0.05], [0.16, 0.15, 0.11]),
            "haze": haze(rng, [0.36, 0.32, 0.26])}  # fmt: skip


def salt_shore(rng: Rng) -> Changes:
    """White salt crusted round dense blue-green water, like the Dead Sea's shore."""
    return {"ground": {"shape": _pan(rng, (0.3, 0.4))},
            "fluid": water(rng, [0.02, 0.08, 0.1], [0.08, 0.22, 0.24]),
            "haze": haze(rng, [0.36, 0.34, 0.3])}  # fmt: skip


# The savannas


def _savanna(rng: Rng, trees: tuple[float, float]) -> Changes:
    shape = {
        "size": between(rng, 0.7, 1.2),
        "bend_spacing": between(rng, 1.2, 2.2),
        "outcrop_share": between(rng, 0.01, 0.04),
    }
    return {"ground": {"shape": shape}, "flora": {"knobs": {"chance": between(rng, *trees)}}}


def serengeti(rng: Rng) -> Changes:
    """Golden grass to the horizon, trees alone, a dry riverbed."""
    return _savanna(rng, (0.004, 0.008)) | {"haze": haze(rng, [0.36, 0.32, 0.24])}


def green_season(rng: Rng) -> Changes:
    """Make the savanna after the rains: green grass, more trees."""
    colors = {"grass_dry": [0.13, 0.15, 0.07], "grass_gold": [0.17, 0.18, 0.08], "grass_green": [0.09, 0.15, 0.06],
              "sand": [0.3, 0.27, 0.22], "rock": [0.17, 0.16, 0.14]}  # fmt: skip
    changes = _savanna(rng, (0.008, 0.012))
    changes["ground"]["colors"] = palette(rng, colors)
    return changes | {"haze": haze(rng, [0.32, 0.35, 0.32])}


def kalahari(rng: Rng) -> Changes:
    """Pale dry grass on red sand, very few trees."""
    colors = {"grass_dry": [0.3, 0.24, 0.17], "grass_gold": [0.33, 0.28, 0.18], "grass_green": [0.2, 0.18, 0.1],
              "sand": [0.38, 0.2, 0.11], "rock": [0.22, 0.14, 0.1]}  # fmt: skip
    changes = _savanna(rng, (0.002, 0.004))
    changes["ground"]["colors"] = palette(rng, colors)
    return changes | {"haze": haze(rng, [0.38, 0.3, 0.24])}


def outback(rng: Rng) -> Changes:
    """Grey-green spinifex on red earth, red rock outcrops."""
    colors = {"grass_dry": [0.18, 0.18, 0.12], "grass_gold": [0.22, 0.2, 0.12], "grass_green": [0.14, 0.16, 0.1],
              "sand": [0.34, 0.15, 0.08], "rock": [0.3, 0.13, 0.07]}  # fmt: skip
    changes = _savanna(rng, (0.002, 0.005))
    changes["ground"]["colors"] = palette(rng, colors)
    changes["ground"]["shape"]["outcrop_share"] = between(rng, 0.04, 0.07)
    return changes | {"haze": haze(rng, [0.36, 0.26, 0.2])}


# The badlands


def _badlands(rng: Rng) -> Changes:
    return {"size": between(rng, 0.6, 1.1), "floor": between(rng, 0.18, 0.32)}


def painted_hills(rng: Rng) -> Changes:
    """Red, ochre and yellow layers, like the Painted Hills."""
    return {"ground": {"shape": _badlands(rng)}, "haze": haze(rng, [0.36, 0.28, 0.22])}


def grey_badlands(rng: Rng) -> Changes:
    """Blue-grey clay hills banded darker, like Utah's."""
    colors = {"band_1": [0.2, 0.21, 0.23], "band_2": [0.26, 0.27, 0.28], "band_3": [0.16, 0.17, 0.19],
              "band_4": [0.3, 0.29, 0.27], "plateau": [0.24, 0.22, 0.19], "sand": [0.28, 0.26, 0.22],
              "green": [0.11, 0.12, 0.08]}  # fmt: skip
    return {"ground": {"shape": _badlands(rng), "colors": palette(rng, colors)}, "haze": haze(rng, [0.32, 0.32, 0.34])}


def cream_badlands(rng: Rng) -> Changes:
    """Cream, tan and pink layers, grass on the flats, like South Dakota's."""
    colors = {"band_1": [0.32, 0.28, 0.22], "band_2": [0.3, 0.2, 0.17], "band_3": [0.26, 0.22, 0.16],
              "band_4": [0.35, 0.32, 0.26], "plateau": [0.16, 0.17, 0.09], "sand": [0.3, 0.27, 0.2],
              "green": [0.14, 0.15, 0.08]}  # fmt: skip
    return {"ground": {"shape": _badlands(rng), "colors": palette(rng, colors)}, "haze": haze(rng, [0.36, 0.33, 0.28])}


def rainbow_hills(rng: Rng) -> Changes:
    """Stripes of red, orange, yellow and green-grey, like Zhangye's."""
    colors = {"band_1": [0.32, 0.12, 0.08], "band_2": [0.34, 0.22, 0.09], "band_3": [0.3, 0.28, 0.14],
              "band_4": [0.18, 0.22, 0.18], "plateau": [0.3, 0.2, 0.12], "sand": [0.3, 0.24, 0.16],
              "green": [0.12, 0.13, 0.07]}  # fmt: skip
    return {"ground": {"shape": _badlands(rng), "colors": palette(rng, colors)}, "haze": haze(rng, [0.36, 0.28, 0.22])}


DAY, DUSK, NIGHT = "day", "dusk", "night"

THEMES: dict[str, Theme] = {
    "salt_flat": Theme(
        "salt_pan", ("Salt", "White", "Bright"), ("Flat", "Pan", "Crust"), (DAY, DUSK), (0.0, 0.2), salt_flat
    ),
    "turquoise_pan": Theme(
        "salt_pan", ("Turquoise", "Mineral", "Clear"), ("Pools", "Pan", "Flats"), (DAY, DUSK), (0.0, 0.2), turquoise_pan
    ),
    "copper_pan": Theme(
        "salt_pan", ("Copper", "Ochre", "Rust"), ("Flats", "Crust", "Pan"), (DAY, DUSK), (0.0, 0.2), copper_pan
    ),
    "clay_pan": Theme(
        "salt_pan", ("Clay", "Dusty", "Dry"), ("Pan", "Flats", "Plain"), (DAY, DUSK), (0.0, 0.2), clay_pan
    ),
    "salt_shore": Theme(
        "salt_pan", ("Salt", "Dead", "Crusted"), ("Shore", "Sea", "Coast"), (DAY, DUSK), (0.0, 0.2), salt_shore
    ),
    "serengeti": Theme(
        "savanna", ("Golden", "Endless", "Sunlit"), ("Plains", "Savanna", "Grasslands"),
        (DAY, DUSK), (0.0, 0.3), serengeti
    ),
    "green_season": Theme(
        "savanna", ("Green", "Rainy", "Lush"), ("Savanna", "Plains", "Veld"), (DAY, DUSK), (0.0, 0.3), green_season
    ),
    "kalahari": Theme(
        "savanna", ("Red", "Thirsty", "Dry"), ("Sands", "Veld", "Plains"), (DAY, DUSK), (0.0, 0.3), kalahari
    ),
    "outback": Theme(
        "savanna", ("Red", "Outback", "Spinifex"), ("Country", "Plains", "Downs"), (DAY, DUSK), (0.0, 0.3), outback
    ),
    "painted_hills": Theme(
        "badlands", ("Painted", "Ochre", "Banded"), ("Hills", "Badlands", "Gullies"),
        (DAY, DUSK), (0.0, 0.3), painted_hills
    ),
    "grey_badlands": Theme(
        "badlands", ("Grey", "Clay", "Ashen"), ("Badlands", "Hills", "Breaks"), (DAY, DUSK), (0.0, 0.3), grey_badlands
    ),
    "cream_badlands": Theme(
        "badlands", ("Cream", "Pink", "Prairie"), ("Badlands", "Walls", "Buttes"),
        (DAY, DUSK), (0.0, 0.3), cream_badlands
    ),
    "rainbow_hills": Theme(
        "badlands", ("Rainbow", "Striped", "Bright"), ("Hills", "Mountains", "Ridges"),
        (DAY, DUSK), (0.0, 0.3), rainbow_hills
    ),
}  # fmt: skip
