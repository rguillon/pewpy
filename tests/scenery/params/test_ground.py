import dataclasses

import pytest

from pewpy.scenery.params.ground import Flora, Fluid, Ground, Outposts, Settlement
from pewpy.scenery.params.presets import resolve


def test_a_ground_has_its_landscape_painter_and_place() -> None:
    ground = resolve("savanna").ground
    assert isinstance(ground, Ground)
    assert (ground.landscape, ground.style) == ("savanna", "savanna")
    assert ground.depth > ground.max_height > 0
    with pytest.raises(dataclasses.FrozenInstanceError):
        ground.depth = 0.0  # ty: ignore[invalid-assignment]


def test_a_ground_can_have_a_fluid_a_settlement_flora_and_outposts() -> None:
    assert isinstance(resolve("salt_pan").fluid, Fluid)
    assert isinstance(resolve("city").settlement, Settlement)
    assert isinstance(resolve("savanna").flora, Flora)
    outposts = resolve("salt_pan").outposts
    assert isinstance(outposts, Outposts)
    assert outposts.kinds
    assert outposts.size[0] <= outposts.size[1]


def test_space_has_no_ground() -> None:
    space = resolve("space")
    assert (space.ground, space.fluid, space.settlement, space.flora, space.outposts) == (None,) * 5
