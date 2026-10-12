from pewpy.scenery.ground.shader.glsl.ground.scatter import GLSL
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_it_defines_its_painting_in_whole_glsl() -> None:
    assert defines(GLSL) == {"nearest"}
    assert balanced(GLSL)
