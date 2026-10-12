from pewpy.scenery.ground.props.model import MATERIALS
from pewpy.scenery.ground.shader.glsl.props import PROP_SHADER
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_the_prop_program_paints_windows_in_its_main() -> None:
    assert defines(PROP_SHADER) == {"window", "main"}
    assert balanced(PROP_SHADER)


def test_the_prop_program_knows_every_material_by_its_number() -> None:
    for name, number in MATERIALS.items():
        if number:
            assert f"const float {name} = {float(number)};" in PROP_SHADER
