"""What the shaders read: the level's colors, the sun, the haze, and the maps over the whole loop."""

import numpy as np
from panda3d.core import LVecBase3f, NodePath, PTA_LVecBase3f, SamplerState, Texture

from pewpy.scenery.ground.relief import SUN_ALONG, SUN_RISE, Relief
from pewpy.scenery.ground.settlement import Layout
from pewpy.scenery.params import FLUID_COLORS, STYLE_COLORS, SceneryParams

# The ground shader's `style`: how it paints each kind of ground (anything else: 0, the mountains).
STYLES = {
    "city": 1.0,
    "refinery": 2.0,
    "farmland": 3.0,
    "planet": 4.0,
    "ocean": 5.0,
    "desert": 6.0,
    "forest": 7.0,
    "canyon": 8.0,
    "pack_ice": 9.0,
    "volcano": 10.0,
    "swamp": 11.0,
    "clouds": 12.0,
    "geysers": 13.0,
}
FLUIDS = {"water": 1.0, "lava": 2.0, "gap": 3.0}
PALETTE_SIZE = 16
# Built-up grounds' colors in the palette: the surface's number (settlement.py Surface) is its slot.
SURFACE_SLOTS = (
    "natural_low",
    "street",
    "pavement",
    "yard",
    "dirt_road",
    "wheat",
    "crop",
    "plowed",
    "lavender",
    "pasture_low",
    "farmyard",
    "natural_high",
    "pasture_high",
    "lamp",
)


def maps(relief: Relief, layout: Layout | None) -> dict[str, Texture]:
    """Make the textures both shaders read over the whole loop.

    The shadow heights and, for built-up grounds, the surface map.
    """
    shadow = Texture("shadow_heights")
    heights = np.ascontiguousarray(relief.shadow_heights, dtype=np.float32)
    shadow.setup2dTexture(heights.shape[1], heights.shape[0], Texture.T_float, Texture.F_r32)
    shadow.setRamImage(heights.tobytes())  # the first row is at v = 0: the loop's start
    shadow.setWrapU(SamplerState.WM_clamp)
    shadow.setWrapV(SamplerState.WM_repeat)
    result = {"shadow_map": shadow}
    if layout is not None:
        surface = Texture("surface")
        texels = np.zeros((*layout.surface.shape, 4), dtype=np.uint8)
        # RGBA textures are kept as blue, green, red, alpha: red is the surface, green the lot's number.
        texels[..., 2] = layout.surface
        texels[..., 1] = layout.variant
        texels[..., 3] = 255
        surface.setup2dTexture(texels.shape[1], texels.shape[0], Texture.T_unsigned_byte, Texture.F_rgba8)
        surface.setRamImage(texels.tobytes())
        surface.setMagfilter(SamplerState.FT_nearest)
        surface.setMinfilter(SamplerState.FT_nearest)
        surface.setWrapU(SamplerState.WM_clamp)
        surface.setWrapV(SamplerState.WM_repeat)
        result["surface_map"] = surface
    return result


def palette(params: SceneryParams) -> list[tuple[float, float, float]]:
    """Return the ground painter's colors, in the slots it reads them from."""
    colors = [(0.0, 0.0, 0.0)] * PALETTE_SIZE
    ground = params.ground
    if ground is None:
        return colors
    if params.settlement is not None and not STYLE_COLORS[ground.style]:  # a built-up ground
        for name, color in params.settlement.colors.items():
            colors[SURFACE_SLOTS.index(name)] = color
    else:
        for slot, name in enumerate(STYLE_COLORS[ground.style]):
            colors[slot] = ground.colors[name]
    return colors


def _colors(colors: list[tuple[float, float, float]]) -> PTA_LVecBase3f:
    array = PTA_LVecBase3f.emptyArray(len(colors))
    for index, color in enumerate(colors):
        array[index] = LVecBase3f(*color)
    return array


def ground_inputs(
    path: NodePath, params: SceneryParams, textures: dict[str, Texture], loop: float, width: float
) -> None:
    """Set what both shaders need on the node above the ground's strips."""
    along_x, along_y = SUN_ALONG
    # Ground directions (x right, y down the screen, z towards the camera) -> model space (x, -z, -y).
    path.setShaderInput("sun", (along_x, -SUN_RISE, -along_y))
    path.setShaderInput("sun_color", params.light.sun)
    path.setShaderInput("sky_color", params.light.sky)
    path.setShaderInput("haze_near", params.haze.near)
    path.setShaderInput("haze_range", params.haze.range)
    path.setShaderInput("ground_loop", loop)
    path.setShaderInput("ground_width", width)
    style = params.ground.style if params.ground else ""
    path.setShaderInput("style", STYLES.get(style, 0.0))
    path.setShaderInput("palette", _colors(palette(params)))
    fluid = params.fluid
    path.setShaderInput("fluid", FLUIDS[fluid.kind] if fluid else 0.0)
    fluid_colors = [(0.0, 0.0, 0.0)] * 3
    if fluid is not None:
        for slot, name in enumerate(FLUID_COLORS[fluid.kind]):
            fluid_colors[slot] = fluid.colors[name]
    path.setShaderInput("fluid_colors", _colors(fluid_colors))
    props = params.props
    path.setShaderInput("window_lights", _colors(list(props.window_lights)))
    path.setShaderInput("glass_color", props.glass)
    path.setShaderInput("furnace_color", props.furnace)
    path.setShaderInput("shadow_map", textures["shadow_map"])
    path.setShaderInput("surface_map", textures.get("surface_map", textures["shadow_map"]))
