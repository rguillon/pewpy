from pewpy.scenery import params
from pewpy.scenery.ground import shader


def test_a_scenery_without_ground_paints_nothing():
    assert set(shader.palette(params.resolve("space"))) == {(0.0, 0.0, 0.0)}


def test_a_ground_has_its_colors():
    assert len(set(shader.palette(params.resolve("forest")))) > 1
