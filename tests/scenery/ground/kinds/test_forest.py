import numpy as np

from pewpy.scenery.ground.kinds.forest import Forest

KNOBS = {"canopy_size": 0.84, "river_spacing": 2.8, "river_width": 0.12}


def test_a_forest_is_a_canopy_with_clearings_and_a_river_below_the_ground() -> None:
    shape = Forest().shape(np.random.default_rng(0), 200, 80, 0.25, 0.02, KNOBS)
    assert shape.marks is not None
    assert float(np.min(shape.marks)) >= 0.0
    assert float(np.max(shape.marks)) <= 1.0
    under_canopy = shape.marks > 0.9
    clearings = shape.marks < 0.1
    assert under_canopy.any()
    assert clearings.any()
    assert float(np.mean(shape.heights[under_canopy])) > float(np.mean(shape.heights[clearings]))
    assert (shape.heights < 0).any()  # the river
    assert float(np.max(shape.heights)) < 0.04 + 0.045 + 1e-9
