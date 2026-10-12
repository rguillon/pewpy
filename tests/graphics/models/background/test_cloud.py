from panda3d.core import ColorBlendAttrib, PNMImage

from pewpy.graphics.models.background.cloud import cloud_model


def test_a_cloud_is_a_glow_of_its_color_fading_to_nothing_at_its_edges() -> None:
    cloud = cloud_model((1.0, 0.0, 0.5, 1.0), seed=2)
    image = PNMImage()
    cloud.getTexture().store(image)
    middle, corner = image.getXel(32, 32), image.getXel(0, 0)
    assert middle[0] > 0
    assert middle[1] == 0
    assert middle[2] > 0
    assert tuple(corner) == (0.0, 0.0, 0.0)
    blend = cloud.getAttrib(ColorBlendAttrib)
    assert isinstance(blend, ColorBlendAttrib)
    assert blend.getMode() == ColorBlendAttrib.MAdd  # added to what's behind
    assert cloud.hasLightOff()


def test_a_clouds_shape_depends_on_its_seed() -> None:
    first, second = PNMImage(), PNMImage()
    cloud_model((1.0, 1.0, 1.0, 1.0), seed=1).getTexture().store(first)
    cloud_model((1.0, 1.0, 1.0, 1.0), seed=2).getTexture().store(second)
    assert first.getXel(20, 20) != second.getXel(20, 20)
