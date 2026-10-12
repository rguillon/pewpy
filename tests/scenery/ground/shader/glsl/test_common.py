from pewpy.scenery.ground.shader.glsl.common import COMMON
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_both_programs_start_with_the_shared_noise_shadows_light_and_haze() -> None:
    assert COMMON.lstrip().startswith("#version 150")
    assert defines(COMMON) == {"hash", "noise", "fbm", "ground_point", "in_shadow", "night", "daylight", "hazy"}
    assert balanced(COMMON)


def test_the_shadows_softness_is_filled_in() -> None:
    assert "%(softness)s" in COMMON
    assert "const float SOFTNESS = 0.5;" in COMMON % {"softness": "0.5"}
