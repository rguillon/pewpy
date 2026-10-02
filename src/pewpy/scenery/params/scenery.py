"""A whole scenery's parameters."""

from dataclasses import dataclass

from pewpy.scenery.params.ground import Flora, Fluid, Ground, Outposts, Settlement
from pewpy.scenery.params.props import PropColors
from pewpy.scenery.params.sky import Haze, Light, Mist, TimeOfDay
from pewpy.scenery.params.space import DistantPlanet, Nebulas, Rocks, Stars
from pewpy.scenery.params.types import Color3


@dataclass(frozen=True)
class SceneryParams:
    """A level's scenery: its sky, light and air, and every layer behind the play area."""

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
    outposts: Outposts | None
