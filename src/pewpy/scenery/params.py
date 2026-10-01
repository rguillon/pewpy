"""What a level's scenery looks like and how it's laid out: the parameters, read from `levels/sceneries.json`.

That file has a "default" entry, what every scenery shares, and one preset per kind of background ("space", "city",
"ocean"...). A level names its preset (`background`) and can change any of its values (`scenery` in its JSON file):
the level's values are merged over the preset's, the preset's over the default's (objects key by key, anything else
replaced; but naming another landscape, painter or generator takes the new one's numbers and colors as given, see
DEPENDS_ON). The result must be complete: the code has no values of its own.

What a scenery has decides what's drawn: stars, nebulas and a distant planet (space), asteroids (debris), or a
ground (its landscape, painted by the ground shader; maybe a fluid below height 0, a settlement on it, flora).
Generators named in the data (a landscape, a settlement, flora) take their own numbers ("knobs"), checked against
what each one needs (see KNOBS in landscapes.py and settlement.py). Colors are [red, green, blue] from 0 to 1.

Independent from Panda3D.
"""

import json
import types
from dataclasses import dataclass, fields, is_dataclass
from functools import cache
from typing import Any, Union, get_args, get_origin, get_type_hints

from pewpy.data import data_folder

Color3 = tuple[float, float, float]
Knobs = dict[str, Any]  # a generator's own numbers (and lists), by name


class SceneryError(ValueError):
    def __init__(self, where: str, problem: str) -> None:
        super().__init__(f"{where}: {problem}" if where else problem)


@dataclass(frozen=True)
class TimeOfDay:
    ground: Color3  # tint of the ground (and what stands on it)
    air: Color3  # tint of the haze and the sky


@dataclass(frozen=True)
class Light:
    sun: Color3
    sky: Color3  # light from the sky, in the open


@dataclass(frozen=True)
class Haze:
    color: Color3  # the air far away
    amount: float  # how much of it, at the farthest
    near: float  # from this distance to the camera (world units)...
    range: float  # ...to this much farther, where it's thickest


@dataclass(frozen=True)
class MistLayer:
    depth: float  # the deepest it goes (world units behind the play plane); over high ground it comes closer...
    above_ground: float  # ...staying at most this share of the way from the ships down to the highest ground
    speed: float  # how fast it moves on screen, as a share of the level's scroll speed


@dataclass(frozen=True)
class Mist:
    """See-through clouds between a ground and the ships, when a level has some (`clouds`)."""

    color: Color3  # pale, mixed with the air's color...
    air: float  # ...this much
    night: float  # how bright they stay when the ground goes dark (lights below still catch them)
    opacity: tuple[float, float]  # each one somewhere between
    layers: tuple[MistLayer, ...]
    count: int  # per layer, with the most clouds (clouds = 1)
    size: tuple[float, float]
    wind: float  # fastest sideways drift, world units per second


@dataclass(frozen=True)
class StarLayer:
    speed: float  # as a share of the scroll speed: far stars are slow...
    size: float  # ...small...
    brightness: float  # ...and dim


@dataclass(frozen=True)
class Stars:
    depth: float
    count: int  # over the play area (more where the layer is bigger)
    layers: tuple[StarLayer, ...]


@dataclass(frozen=True)
class Nebulas:
    depth: float
    speed: float
    count: int
    size: tuple[float, float]
    palettes: tuple[tuple[Color3, ...], ...]  # one is picked by the level's background seed


@dataclass(frozen=True)
class DistantPlanet:
    depth: float
    speed: float
    size: tuple[float, float]
    spin: float  # degrees per second
    palettes: tuple[tuple[Color3, ...], ...]  # its bands; one is picked by the level's background seed


@dataclass(frozen=True)
class RockLayer:
    depth: float
    count: int
    size: tuple[float, float]
    speed: float


@dataclass(frozen=True)
class Rocks:
    layers: tuple[RockLayer, ...]
    spin: float  # fastest tumble, degrees per second
    colors: tuple[Color3, ...]  # each voxel of an asteroid picks one


@dataclass(frozen=True)
class Ground:
    landscape: str  # its shape (landscapes.py LANDSCAPES)...
    shape: Knobs  # ...and that landscape's numbers
    style: str  # how the ground shader paints it (ground_shader.py STYLES)...
    colors: dict[str, Color3]  # ...with these colors (STYLE_COLORS names them; built-up grounds: the settlement's)
    depth: float  # its base layer, world units behind the play plane; it rises towards the camera from there...
    max_height: float  # ...this high at most (keep depth - max_height > 0.1: behind the ships)


@dataclass(frozen=True)
class Fluid:
    """What's below height 0: "water", "lava" or "gap" (in a cloud deck: the ground far below)."""

    kind: str
    colors: dict[str, Color3]  # see ground_shader.py FLUID_COLORS


@dataclass(frozen=True)
class Settlement:
    """Streets, fields, yards painted on the ground, and what stands on them (settlement.py)."""

    kind: str  # settlement.py SETTLEMENTS
    colors: dict[str, Color3]  # of what covers the ground (ground_shader.py SURFACE_COLORS)
    layout: Knobs  # the settlement's numbers


@dataclass(frozen=True)
class Flora:
    """Sparse props placed from the landscape's shape (landscapes.py FLORAS)."""

    kind: str
    knobs: Knobs


@dataclass(frozen=True)
class PropColors:
    """The props standing on the grounds (props/); lists: each one picks among them. Each prop varies its
    colors a little around these.
    """

    building_walls: tuple[Color3, ...]
    roofs: tuple[Color3, ...]
    roof_unit: Color3
    beacon: Color3
    window_lights: tuple[Color3, Color3]  # most windows lit with the first, some with the second
    glass: Color3  # unlit windows
    refinery_metals: tuple[Color3, ...]
    plant_walls: Color3
    plant_roof: Color3
    furnace: Color3  # the glow of its windows
    stack: Color3
    flame: Color3
    pipe: Color3
    house_walls: Color3
    house_roofs: tuple[Color3, ...]
    barn_walls: Color3
    barn_roof: Color3
    silo: Color3
    trees: tuple[Color3, ...]
    hedge: Color3
    palm_fronds: Color3
    palm_trunk: Color3
    dead_wood: Color3
    concrete: Color3  # cooling towers
    glasshouse: Color3  # greenhouses
    vent: Color3  # dark openings: a cooling tower's inside, a chimney's mouth


@dataclass(frozen=True)
class SceneryParams:
    name: str  # the preset's
    sky: Color3  # what shows where nothing is drawn (between clouds, around space)
    light: Light
    haze: Haze
    times_of_day: dict[str, TimeOfDay]
    mist: Mist
    props: PropColors
    stars: Stars | None
    nebulas: Nebulas | None
    planet: DistantPlanet | None
    rocks: Rocks | None
    ground: Ground | None
    fluid: Fluid | None
    settlement: Settlement | None
    flora: Flora | None


# What depends on which generator or painter an object names: when `over` names another one, these are replaced by
# `over`'s (the new one's numbers and colors), not merged with the old one's.
DEPENDS_ON = {"landscape": ("shape",), "style": ("colors",), "kind": ("layout", "knobs", "colors")}


def merge(base: Any, over: Any) -> Any:
    """`over` on top of `base`: objects merged key by key, anything else replaced."""
    if isinstance(base, dict) and isinstance(over, dict):
        merged = dict(base)
        for key, value in over.items():
            merged[key] = merge(base[key], value) if key in base else value
        for name, dependents in DEPENDS_ON.items():
            if name in base and name in over and base[name] != over[name]:
                for key in dependents:
                    if key in base:
                        merged[key] = over.get(key, {})
        return merged
    return over


def _number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SceneryError(where, f"expected a number, not {value!r}")
    return float(value)


def _convert(kind: Any, value: Any, where: str) -> Any:  # noqa: C901 - one case per kind of type
    """`value` (decoded JSON) as `kind`, a type of the dataclasses above."""
    origin, args = get_origin(kind), get_args(kind)
    if origin in (Union, types.UnionType):  # X | None
        if value is None:
            return None
        return _convert(next(arg for arg in args if arg is not type(None)), value, where)
    if value is None:
        raise SceneryError(where, "missing (null)")
    if is_dataclass(kind) and isinstance(kind, type):
        return build(kind, value, where)
    if kind is float:
        return _number(value, where)
    if kind is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SceneryError(where, f"expected a whole number, not {value!r}")
        return value
    if kind is str:
        if not isinstance(value, str):
            raise SceneryError(where, f"expected a name, not {value!r}")
        return value
    if origin is tuple:
        if not isinstance(value, list):
            raise SceneryError(where, f"expected a list, not {value!r}")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_convert(args[0], item, f"{where}[{i}]") for i, item in enumerate(value))
        if len(value) != len(args):
            raise SceneryError(where, f"expected {len(args)} values, not {len(value)}")
        return tuple(_convert(arg, item, f"{where}[{i}]") for i, (arg, item) in enumerate(zip(args, value)))  # noqa: B905
    if origin is dict:
        if not isinstance(value, dict):
            raise SceneryError(where, f"expected an object, not {value!r}")
        return {key: _convert(args[1], item, f"{where}.{key}") for key, item in value.items()}
    if kind is Any:
        return value
    raise SceneryError(where, f"can't read a {kind}")  # pragma: no cover - a type the dataclasses don't use


def build(cls: Any, data: Any, where: str = "", given: dict[str, Any] | None = None) -> Any:
    """A dataclass from decoded JSON: every field there, nothing else (but the fields `given`)."""
    if not isinstance(data, dict):
        raise SceneryError(where, f"expected an object, not {data!r}")
    given = given or {}
    hints = get_type_hints(cls)
    names = {field.name for field in fields(cls)} - set(given)
    unknown = set(data) - names
    if unknown:
        raise SceneryError(where, f"unknown keys {sorted(unknown)}, expected some of {sorted(names)}")
    missing = names - set(data)
    if missing:
        raise SceneryError(where, f"missing {sorted(missing)}")
    values = {name: _convert(hints[name], data[name], f"{where}.{name}" if where else name) for name in names}
    return cls(**values, **given)


@cache
def presets() -> dict[str, Any]:
    """The decoded `levels/sceneries.json`: "default" and the presets."""
    return json.loads(data_folder().joinpath("levels").joinpath("sceneries.json").read_text())


def backgrounds() -> tuple[str, ...]:
    """The presets' names, in the file's order."""
    return tuple(name for name in presets() if name != "default")


def resolve(background: str, overrides: dict[str, Any] | None = None) -> SceneryParams:
    """The parameters of preset `background` with a level's `overrides`, checked (SceneryError if they're wrong)."""
    data = presets()
    if background not in data or background == "default":
        raise SceneryError("", f"unknown background {background!r}, expected one of {sorted(backgrounds())}")
    merged = merge(merge(data["default"], data[background]), overrides or {})
    params = build(SceneryParams, merged, background, given={"name": background})
    _check_generators(params)
    return params


def _check_generators(params: SceneryParams) -> None:
    """The generators and painters named exist, and get the numbers and colors they need."""
    from pewpy.scenery import landscapes, settlement

    name = params.name
    if params.ground is not None:
        _check_knobs(params.ground.landscape, params.ground.shape, landscapes.KNOBS, f"{name}.ground.shape")
        _check_names(params.ground.style, params.ground.colors, STYLE_COLORS, f"{name}.ground.colors")
    if params.fluid is not None:
        _check_names(params.fluid.kind, params.fluid.colors, FLUID_COLORS, f"{name}.fluid.colors")
    if params.settlement is not None:
        _check_knobs(params.settlement.kind, params.settlement.layout, settlement.KNOBS, f"{name}.settlement.layout")
        _check_names(params.settlement.kind, params.settlement.colors, SURFACE_COLORS, f"{name}.settlement.colors")
    if params.flora is not None:
        _check_knobs(params.flora.kind, params.flora.knobs, landscapes.FLORA_KNOBS, f"{name}.flora.knobs")


def _check_knobs(kind: str, knobs: Knobs, needed: dict[str, tuple[str, ...]], where: str) -> None:
    if kind not in needed:
        raise SceneryError(where, f"unknown {kind!r}, expected one of {sorted(needed)}")
    _exactly(set(knobs), set(needed[kind]), where)


def _check_names(kind: str, colors: dict[str, Color3], names: dict[str, tuple[str, ...]], where: str) -> None:
    if kind not in names:
        raise SceneryError(where, f"unknown {kind!r}, expected one of {sorted(names)}")
    _exactly(set(colors), set(names[kind]), where)


def _exactly(given: set[str], needed: set[str], where: str) -> None:
    if given - needed:
        raise SceneryError(where, f"unknown {sorted(given - needed)}, expected {sorted(needed)}")
    if needed - given:
        raise SceneryError(where, f"missing {sorted(needed - given)}")


# The colors each of the ground shader's painters uses (ground.colors), in the order it reads them; built-up grounds
# ("city", "refinery", "farmland") paint the settlement's surfaces with its colors instead (settlement.colors).
STYLE_COLORS: dict[str, tuple[str, ...]] = {
    "mountains": ("rock_low", "rock_high", "scree", "meadow_low", "meadow_high", "pine", "snow"),
    "city": (),
    "refinery": (),
    "farmland": (),
    "planet": ("low", "high", "rims"),
    "ocean": ("beach", "grass", "trees", "rock"),
    "desert": ("sand_low", "sand_high", "rock_a", "rock_b", "rock_top", "grass"),
    "forest": ("tree_a", "tree_b", "tree_c", "clearing_low", "clearing_high"),
    "canyon": ("band_1", "band_2", "band_3", "band_4", "plateau", "sand", "green"),
    "pack_ice": ("floe", "berg_low", "berg_high"),
    "volcano": ("rock", "ash", "glow"),
    "swamp": ("mud", "reeds_low", "reeds_high"),
    "clouds": ("shade", "lit"),
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
    "lava": ("hot", "crust"),
    "gap": ("below", "light_a", "light_b"),  # the ground far below, and the two colors of its town lights
}
