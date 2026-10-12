from panda3d.core import PNMImage

from pewpy.graphics.models.background.mist import MIST_TEXTURES, mist_model


def test_mist_is_see_through_white_fading_at_its_edges() -> None:
    mist = mist_model(0)
    image = PNMImage()
    mist.getTexture().store(image)
    assert tuple(image.getXel(32, 32)) == (1.0, 1.0, 1.0)
    assert image.getAlpha(32, 32) > 0
    assert image.getAlpha(0, 0) == 0
    assert mist.hasTransparency()
    assert mist.getTwoSided()


def test_mist_comes_in_a_few_shapes_built_once() -> None:
    assert mist_model(1 + MIST_TEXTURES).getTexture().getName() == "mist_1"
    assert mist_model(1).getTexture() == mist_model(1).getTexture()
    assert mist_model(2).getTexture().getName() == "mist_2"
