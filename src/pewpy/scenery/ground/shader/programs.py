"""The shaders, compiled from their GLSL programs (glsl/)."""

from panda3d.core import Shader

from pewpy.scenery.ground.relief import SHADOW_SOFTNESS
from pewpy.scenery.ground.shader.glsl.common import COMMON
from pewpy.scenery.ground.shader.glsl.ground import GROUND_SHADER
from pewpy.scenery.ground.shader.glsl.props import PROP_SHADER
from pewpy.scenery.ground.shader.glsl.vertex import VERTEX_SHADER
from pewpy.scenery.ground.shader.inputs import PALETTE_SIZE

_shaders: dict[str, Shader] = {}


def shader(name: str) -> Shader:
    """Compiled once, shared by every strip."""
    if name not in _shaders:
        common = COMMON % {"softness": repr(SHADOW_SOFTNESS)}
        body = GROUND_SHADER % {"palette": PALETTE_SIZE} if name == "ground" else PROP_SHADER
        _shaders[name] = Shader.make(Shader.SL_GLSL, VERTEX_SHADER, common + body)
    return _shaders[name]
