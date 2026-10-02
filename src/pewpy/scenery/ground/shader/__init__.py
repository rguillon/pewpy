"""Drawing the smooth grounds of relief.py, and the props standing on the built-up ones.

Fine meshes painted by shaders (programs.py, from glsl/: one module per painter) on meshes (geometry.py).

The ground shader works out what the ground is made of at every pixel. On natural grounds (the mountains): from
the height, the slope, how tucked-in the spot is (the relief's cavity) and procedural noise: rock with strata,
scree, snow, meadows, pines. On built-up grounds: from the layout's surface map (settlement.py: streets, pavements,
yards, fields...). Fine noise also bends the normal, so surfaces look rough at any distance.

The prop shader paints buildings, tanks, trees... from each face's material (props/): rows of windows
(more of them lit at dusk and night), glowing furnaces, flames and beacons, metal sheen, leafy crowns.

Their colors come from the level's scenery (pewpy.scenery.params), as shader inputs (inputs.py): each painter reads
its colors from `palette` in the order STYLE_COLORS names them (built-up grounds: the settlement's, by surface, see
SURFACE_SLOTS), the fluid's from `fluid_colors`.

Both light with the same low sun, whose shadows (from the ground and from the props) are baked in a map of how
high the shadows reach (relief.py), read pixel by pixel: towers shade the streets and the roofs next to them.
Sky light, the level's haze and its time-of-day tint work like on the rest of the scene. The noise and the maps
loop with the ground (`ground_loop`), so there is no seam where the loop starts again.
"""

from pewpy.scenery.ground.shader.geometry import props_model, relief_chunk_model
from pewpy.scenery.ground.shader.inputs import FLUIDS, PALETTE_SIZE, STYLES, SURFACE_SLOTS, ground_inputs, maps, palette

__all__ = [
    "FLUIDS",
    "PALETTE_SIZE",
    "STYLES",
    "SURFACE_SLOTS",
    "ground_inputs",
    "maps",
    "palette",
    "props_model",
    "relief_chunk_model",
]
