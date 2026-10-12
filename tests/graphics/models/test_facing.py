import math

import pytest
from panda3d.core import NodePath, Vec3

from pewpy.graphics.models.facing import facing_roll


@pytest.mark.parametrize(("dx", "dz"), [(0, -1), (1, 0), (-1, 0), (0, 1), (1, -1), (-0.3, 0.7)])
def test_facing_roll_points_the_model_along_the_direction(dx: float, dz: float) -> None:
    root = NodePath("root")
    model = root.attachNewNode("model")
    model.setR(facing_roll(dx, dz))
    front = root.getRelativeVector(model, Vec3(0, 0, -1))  # models point down the screen
    length = math.hypot(dx, dz)
    assert front.x == pytest.approx(dx / length, abs=1e-5)
    assert front.z == pytest.approx(dz / length, abs=1e-5)
