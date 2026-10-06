"""The props' lights: how the prop shader paints their windows and furnaces."""

from dataclasses import dataclass

from pewpy.scenery.params.types import Color3


@dataclass(frozen=True)
class PropColors:
    """The lights of the props standing on the grounds (props/), painted by the shader from their materials.

    The props' own colors are fixed in their descriptions (data/models/props/).
    """

    window_lights: tuple[Color3, Color3]  # most windows lit with the first, some with the second
    glass: Color3  # unlit windows
    furnace: Color3  # the glow of its windows
