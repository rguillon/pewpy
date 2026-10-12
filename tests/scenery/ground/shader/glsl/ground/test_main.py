import pytest

from pewpy.scenery.ground.shader.glsl.ground.main import GLSL
from pewpy.scenery.ground.shader.inputs import STYLES
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_main_paints_lights_and_hazes_the_ground() -> None:
    assert defines(GLSL) == {"main"}
    assert balanced(GLSL)
    assert "fragment_color = vec4(hazy(lit), 1.0);" in GLSL


@pytest.mark.parametrize(("style", "number"), [(style, number) for style, number in STYLES.items() if number > 3.5])
def test_main_picks_the_painter_of_each_natural_style(style: str, number: float) -> None:
    assert f"style == {number})" in GLSL
    assert f"ground = {style}(" in GLSL


def test_built_up_grounds_share_a_painter_and_anything_else_is_mountains() -> None:
    built_up = [number for style, number in STYLES.items() if style in ("city", "refinery", "farmland")]
    assert max(built_up) < 3.5
    assert "style > 0.5 && style < 3.5) {\n        ground = built_up(" in GLSL
    assert "} else {\n        ground = mountains(" in GLSL


def test_fluid_covers_the_ground_below_height_0() -> None:
    assert "lit = mix(lit, fluid_surface(" in GLSL
