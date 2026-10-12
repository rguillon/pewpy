import re
from dataclasses import replace

import pytest

from pewpy.scenery.params.checks import check_generators
from pewpy.scenery.params.ground import Flora, Outposts
from pewpy.scenery.params.presets import backgrounds, resolve
from pewpy.scenery.params.types import SceneryError


@pytest.mark.parametrize("name", backgrounds())
def test_every_preset_names_generators_and_painters_that_exist(name: str) -> None:
    check_generators(resolve(name))


def test_a_grounds_landscape_and_its_numbers_are_checked() -> None:
    salt_pan = resolve("salt_pan")
    ground = salt_pan.ground
    assert ground is not None
    with pytest.raises(SceneryError, match=re.escape("salt_pan.ground.shape: unknown 'lakes'")):
        check_generators(replace(salt_pan, ground=replace(ground, landscape="lakes")))
    with pytest.raises(SceneryError, match=re.escape("salt_pan.ground.shape: missing ['pool_share']")):
        check_generators(replace(salt_pan, ground=replace(ground, shape={"size": 0.5})))
    with pytest.raises(SceneryError, match=re.escape("salt_pan.ground.shape: unknown ['x']")):
        check_generators(replace(salt_pan, ground=replace(ground, shape={**ground.shape, "x": 1})))


def test_a_grounds_painter_and_its_fluid_are_checked() -> None:
    salt_pan = resolve("salt_pan")
    assert salt_pan.ground is not None
    assert salt_pan.fluid is not None
    with pytest.raises(SceneryError, match=re.escape("salt_pan.ground.colors: unknown 'chalk'")):
        check_generators(replace(salt_pan, ground=replace(salt_pan.ground, style="chalk")))
    with pytest.raises(SceneryError, match=re.escape("salt_pan.fluid.colors: unknown 'lava'")):
        check_generators(replace(salt_pan, fluid=replace(salt_pan.fluid, kind="lava")))


def test_a_settlement_and_its_colors_are_checked() -> None:
    city = resolve("city")
    assert city.settlement is not None
    with pytest.raises(SceneryError, match=re.escape("city.settlement.layout: unknown 'village'")):
        check_generators(replace(city, settlement=replace(city.settlement, kind="village")))
    colors = {name: color for name, color in city.settlement.colors.items() if name != "lamp"}
    with pytest.raises(SceneryError, match=re.escape("city.settlement.colors: missing ['lamp']")):
        check_generators(replace(city, settlement=replace(city.settlement, colors=colors)))


def test_flora_and_outposts_are_checked() -> None:
    savanna = resolve("savanna")
    with pytest.raises(SceneryError, match=re.escape("savanna.flora.knobs: unknown 'palms'")):
        check_generators(replace(savanna, flora=Flora("palms", {})))
    with pytest.raises(SceneryError, match=re.escape("savanna.outposts.kinds: unknown ['castle']")):
        check_generators(replace(savanna, outposts=Outposts(("castle",), 1.0, (0.2, 0.3))))
    with pytest.raises(SceneryError, match=re.escape("savanna.outposts.kinds: unknown []")):
        check_generators(replace(savanna, outposts=Outposts((), 1.0, (0.2, 0.3))))
