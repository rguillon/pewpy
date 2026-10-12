import random

from pewpy.scenery import params
from pewpy.scenery.background.layers.mist import mist_layer
from tests.scenery.background.views import AREA


def test_mist_comes_in_the_amount_asked_blown_by_the_wind() -> None:
    mist = params.resolve("forest").mist
    layer = mist_layer(random.Random(0), AREA, 0.5, mist, 1.2, 1.0, 0.1)
    assert (layer.kind, layer.depth, len(layer.drifters)) == ("mist", 1.2, mist.count)
    for cloud in layer.drifters:
        assert 0.08 <= cloud.wind <= 0.12
        assert 0.45 <= cloud.speed_factor <= 0.55
        assert AREA.bottom <= cloud.y <= AREA.top
    assert len(mist_layer(random.Random(0), AREA, 0.5, mist, 1.2, 0.5, 0.1).drifters) == round(mist.count / 2)


def test_no_mist_with_no_amount() -> None:
    assert mist_layer(random.Random(0), AREA, 0.5, params.resolve("forest").mist, 1.2, 0.0, 0.1).drifters == []
