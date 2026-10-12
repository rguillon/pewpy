import numpy as np

from pewpy.scenery.ground.kinds.level_ground import LevelGround


def test_level_ground_is_nearly_flat_not_perfectly_even() -> None:
    shape = LevelGround().shape(np.random.default_rng(0), 100, 60, 0.55, 0.02, {"height": 0.006, "size": 0.8})
    assert shape.heights.shape == (100, 60)
    assert 0.0 <= float(np.min(shape.heights)) < float(np.max(shape.heights)) <= 0.006
    assert shape.marks is None
