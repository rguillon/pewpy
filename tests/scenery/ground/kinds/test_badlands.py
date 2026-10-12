import numpy as np
import pytest

from pewpy.scenery.ground.kinds.badlands import Badlands

KNOBS = {"size": 0.8, "floor": 0.25}


def test_badlands_rise_in_ridges_from_flat_sandy_floors() -> None:
    shape = Badlands().shape(np.random.default_rng(0), 200, 80, 0.3, 0.02, KNOBS)
    assert float(np.max(shape.heights)) == pytest.approx(0.3 + 0.004)
    assert np.isclose(shape.heights, 0.004).any()  # flat floors
    assert shape.marks is not None
    assert set(np.unique(shape.marks)) == {0.0, 0.5}
    assert (shape.marks[shape.heights <= 0.004 + 1e-9] == 0.5).all()  # the floors are sand
