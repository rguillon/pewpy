from pewpy.scenery.ground.shader.glsl.ground.salt_pan import GLSL
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_it_defines_its_painting_in_whole_glsl() -> None:
    assert defines(GLSL) == {"plates", "salt_pan"}
    assert balanced(GLSL)
