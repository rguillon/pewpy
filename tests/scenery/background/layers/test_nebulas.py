import random

from pewpy.scenery import params
from pewpy.scenery.background.layers.nebulas import nebula_layer
from tests.scenery.background.views import AREA


def test_nebulas_are_spread_down_the_area_at_their_depth() -> None:
    nebulas = params.resolve("space").nebulas
    assert nebulas is not None
    layer = nebula_layer(random.Random(0), nebulas, AREA)
    assert (layer.kind, layer.depth, len(layer.drifters)) == ("cloud", nebulas.depth, nebulas.count)
    for cloud in layer.drifters:
        assert AREA.left <= cloud.x <= AREA.right
        assert AREA.bottom <= cloud.y <= AREA.top
        assert nebulas.size[0] <= cloud.size <= nebulas.size[1]
        assert cloud.speed_factor == nebulas.speed
    assert [cloud.y for cloud in layer.drifters] == sorted(cloud.y for cloud in layer.drifters)
    assert {cloud.shape for cloud in layer.drifters} <= {0, 1, 2}
