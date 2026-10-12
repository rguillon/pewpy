import numpy as np

from pewpy.scenery.ground.kinds.rolling import Rolling

KNOBS = {"height": 0.035, "swell_size": 1.4, "detail_size": 0.5}


def test_rolling_ground_swells_gently_to_its_height_whatever_stands_on_it() -> None:
    low = Rolling().shape(np.random.default_rng(0), 200, 80, 0.2, 0.02, KNOBS).heights
    high = Rolling().shape(np.random.default_rng(0), 200, 80, 5.0, 0.02, KNOBS).heights
    assert 0.0 <= float(np.min(low)) < float(np.max(low)) <= 0.035
    assert np.array_equal(low, high)  # the highest point is for what stands on it
    assert float(np.max(np.abs(np.diff(low, axis=0)))) < 0.002  # gentle
