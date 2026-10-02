import math

import pytest
from panda3d.core import NodePath

from pewpy.graphics import models
from pewpy.ui import showcase
from pewpy.ui.showcase import ModelShowcase


def make_showcase(count: int = 6) -> ModelShowcase:
    camera = NodePath("camera")
    return ModelShowcase([(f"model {i}", models.model("drone")) for i in range(count)], camera)


def test_models_sit_on_a_circle_in_front_of_the_camera():
    show = make_showcase()
    assert show.root.getY() == pytest.approx(showcase.DISTANCE)
    for slot in show.slots:
        position = slot.getPos(show.root)
        assert math.hypot(position.x, position.z) == pytest.approx(showcase.RADIUS)
        assert position.y == pytest.approx(0.0)
    assert show.slots[0].getPos(show.root).z == pytest.approx(showcase.RADIUS)  # the first one at the top


def test_the_circle_turns_while_models_spin_and_stay_upright():
    show = make_showcase()
    show.update(2.0)
    first = show.slots[0].getPos(show.root)
    angle = math.pi / 2 - math.radians(2.0 * showcase.TURN_SPEED)  # it started at the top and went clockwise
    assert (first.x, first.z) == pytest.approx((math.cos(angle) * showcase.RADIUS, math.sin(angle) * showcase.RADIUS))
    for slot, spinner in zip(show.slots, show.spinners, strict=True):
        assert slot.getR(show.root) == pytest.approx(0.0, abs=1e-4)  # upright, with its name under it
        turned = (spinner.getH() - 2.0 * showcase.SPIN_SPEED) % 360
        assert min(turned, 360 - turned) == pytest.approx(0.0, abs=1e-3)  # spun by 2 s of SPIN_SPEED


def test_every_model_has_its_name():
    show = make_showcase(3)
    assert [slot.getName() for slot in show.slots] == ["model 0", "model 1", "model 2"]
    show.destroy()
    assert show.root.isEmpty()


def test_a_stretched_circle_is_wider_than_tall():
    camera = NodePath("camera")
    show = ModelShowcase([(f"model {i}", models.model("drone")) for i in range(4)], camera, radius=0.5, stretch=2.0)
    xs = [abs(slot.getPos(show.root).x) for slot in show.slots]
    zs = [abs(slot.getPos(show.root).z) for slot in show.slots]
    assert max(xs) == pytest.approx(1.0) and max(zs) == pytest.approx(0.5)
