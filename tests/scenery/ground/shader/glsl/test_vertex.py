from pewpy.scenery.ground.shader.glsl.vertex import VERTEX_SHADER
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_the_vertex_program_passes_the_meshes_data_on() -> None:
    assert VERTEX_SHADER.lstrip().startswith("#version 150")
    assert defines(VERTEX_SHADER) == {"main"}
    assert balanced(VERTEX_SHADER)
    for passed in ("v_position", "v_normal", "v_model", "v_data", "v_wall"):
        assert f" {passed} = " in VERTEX_SHADER
