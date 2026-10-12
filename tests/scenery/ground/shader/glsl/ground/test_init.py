from pewpy.scenery.ground.shader.glsl.ground import GROUND_SHADER, PIECES, main, uniforms
from pewpy.scenery.ground.shader.inputs import PALETTE_SIZE
from tests.scenery.ground.shader.glsl.sources import balanced, defines


def test_the_ground_program_is_its_pieces_inputs_first_main_last() -> None:
    assert "".join(piece.GLSL for piece in PIECES) == GROUND_SHADER
    assert (PIECES[0], PIECES[-1]) == (uniforms, main)
    assert balanced(GROUND_SHADER)


def test_no_two_pieces_define_the_same_function() -> None:
    names = [name for piece in PIECES for name in defines(piece.GLSL)]
    assert len(names) == len(set(names))


def test_the_palettes_size_is_filled_in() -> None:
    assert f"palette[{PALETTE_SIZE}]" in GROUND_SHADER % {"palette": PALETTE_SIZE}
