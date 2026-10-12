import numpy as np

from pewpy.scenery.ground.kinds.salt_pan import SaltPan


def test_a_salt_pan_is_a_flat_crust_with_pools_in_its_hollows() -> None:
    shape = SaltPan().shape(np.random.default_rng(0), 200, 80, 0.1, 0.02, {"size": 0.8, "pool_share": 0.15})
    pools = shape.heights < 0
    assert 0.1 < float(np.mean(pools)) < 0.2
    assert float(np.max(shape.heights)) < 0.05
    assert shape.marks is not None
    assert (shape.marks[pools] == 0.0).all()  # at the shore and below
    assert float(np.max(shape.marks)) == 1.0  # well away from the pools
