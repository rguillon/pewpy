import numpy as np
import pytest

from pewpy.scenery.ground import settlement
from pewpy.scenery.ground.settlement import Prop


def test_props_stand_on_the_lowest_ground_under_them_and_rise_above_it_for_shadows():
    heights = np.zeros((40, 40))
    heights[8:17, 8:17] = np.linspace(0.02, 0.06, 9)[None, :]  # a slope rising to the right
    prop = Prop("building", x=0.24, y=0.24, width=0.06, length=0.06, height=0.2, seed=1)
    (placed,) = settlement.place([prop], heights, 0.02, 0.02)
    assert placed.base == pytest.approx(heights[12, 10])  # the low side of its footprint
    solid = settlement.occluders([placed], heights, 0.02, 0.02)
    assert solid[12, 12] == pytest.approx(heights[12, 10] + 0.2)
    assert solid[30, 30] == 0.0
