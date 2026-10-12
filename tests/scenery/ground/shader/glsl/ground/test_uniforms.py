from pewpy.scenery.ground.shader.glsl.ground.uniforms import GLSL
from pewpy.scenery.ground.shader.inputs import PALETTE_SIZE
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_the_ground_reads_its_style_fluid_colors_and_surface_map() -> None:
    assert defines(GLSL) == set()
    assert balanced(GLSL)
    filled = GLSL % {"palette": PALETTE_SIZE}
    for uniform in ("float style;", "float fluid;", f"vec3 palette[{PALETTE_SIZE}];", "sampler2D surface_map;"):
        assert f"uniform {uniform}" in filled
