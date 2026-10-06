"""What a level's scenery looks like and how it's laid out: the parameters, read from `levels/sceneries.json`.

That file has a "default" entry, what every scenery shares, and one preset per kind of background ("space", "city",
"ocean"...). A level names its preset (`background`) and can change any of its values (`scenery` in its JSON file):
the level's values are merged over the preset's, the preset's over the default's (objects key by key, anything else
replaced; but naming another landscape, painter or generator takes the new one's numbers and colors as given, see
DEPENDS_ON). The result must be complete: the code has no values of its own.

What a scenery has decides what's drawn: stars, nebulas and a distant planet (space), asteroids (debris), or a
ground (its landscape, painted by the ground shader; maybe a fluid below height 0, a settlement on it, flora,
outposts).
Generators named in the data (a landscape, a settlement, flora) take their own numbers ("knobs"), checked against
what each one needs (its `knobs`, see grounds/). Colors are [red, green, blue] from 0 to 1.

Each part of a scenery is a dataclass in its own module (sky.py, space.py, ground.py, props.py, scenery.py);
reader.py reads them, presets.py resolves a level's, checks.py checks the generators.

Independent from Panda3D.
"""

from pewpy.scenery.params.checks import check_generators
from pewpy.scenery.params.colors import FLUID_COLORS, STYLE_COLORS, SURFACE_COLORS
from pewpy.scenery.params.ground import Flora, Fluid, Ground, Outposts, Settlement
from pewpy.scenery.params.presets import backgrounds, presets, resolve
from pewpy.scenery.params.props import PropColors
from pewpy.scenery.params.reader import DEPENDS_ON, build, merge
from pewpy.scenery.params.scenery import SceneryParams
from pewpy.scenery.params.sky import Haze, Light, Mist, MistLayer, TimeOfDay
from pewpy.scenery.params.space import DistantPlanet, Nebulas, StarLayer, Stars
from pewpy.scenery.params.types import Color3, Knobs, SceneryError

__all__ = [
    "DEPENDS_ON",
    "FLUID_COLORS",
    "STYLE_COLORS",
    "SURFACE_COLORS",
    "Color3",
    "DistantPlanet",
    "Flora",
    "Fluid",
    "Ground",
    "Haze",
    "Knobs",
    "Light",
    "Mist",
    "MistLayer",
    "Nebulas",
    "Outposts",
    "PropColors",
    "SceneryError",
    "SceneryParams",
    "Settlement",
    "StarLayer",
    "Stars",
    "TimeOfDay",
    "backgrounds",
    "build",
    "check_generators",
    "merge",
    "presets",
    "resolve",
]
