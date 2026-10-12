from panda3d.core import Shader

from pewpy.scenery.ground.shader.inputs import PALETTE_SIZE
from pewpy.scenery.ground.shader.programs import shader


def test_each_shader_is_made_once_and_shared() -> None:
    assert shader("ground") is shader("ground")
    assert shader("props") is not shader("ground")


def test_the_shaders_are_glsl_with_their_sizes_filled_in() -> None:
    ground = shader("ground")
    assert ground.getLanguage() == Shader.SL_GLSL
    fragment = ground.getText(Shader.ST_fragment)
    assert f"palette[{PALETTE_SIZE}]" in fragment
    assert "%(" not in fragment
    assert "window(" in shader("props").getText(Shader.ST_fragment)
