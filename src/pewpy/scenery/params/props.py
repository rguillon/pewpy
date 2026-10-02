"""The props' colors."""

from dataclasses import dataclass

from pewpy.scenery.params.types import Color3


@dataclass(frozen=True)
class PropColors:
    """The props' colors: the props standing on the grounds (props/).

    Lists: each one picks among them. Each prop varies its colors a little around these.
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
    apron: Color3  # the concrete under the outposts, landing pads
    marking: Color3  # lines painted on aprons and landing pads
    hull: tuple[Color3, ...]  # sci-fi panels: domes, radars, pylons, parked craft
    hangar_walls: tuple[Color3, ...]
    containers: tuple[Color3, ...]
    scifi_light: Color3  # glowing bands, pad lights, pylon crystals
