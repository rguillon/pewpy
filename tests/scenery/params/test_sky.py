import dataclasses

import pytest

from pewpy.scenery.params.presets import backgrounds, resolve
from pewpy.scenery.params.sky import Haze, Light, Mist, MistLayer, TimeOfDay


def test_every_scenery_has_its_light_air_times_of_day_and_mist() -> None:
    for name in backgrounds():
        scenery = resolve(name)
        assert isinstance(scenery.light, Light)
        assert isinstance(scenery.haze, Haze)
        assert isinstance(scenery.mist, Mist)
        assert all(isinstance(time, TimeOfDay) for time in scenery.times_of_day.values())
        assert "day" in scenery.times_of_day


def test_the_haze_starts_near_and_thickens_farther() -> None:
    haze = resolve("savanna").haze
    assert haze.near > 0
    assert haze.range > 0
    assert 0 <= haze.amount <= 1


def test_mist_layers_drift_at_their_depth() -> None:
    mist = resolve("forest").mist
    assert all(isinstance(layer, MistLayer) and layer.depth > 0 for layer in mist.layers)
    assert mist.opacity[0] <= mist.opacity[1]
    with pytest.raises(dataclasses.FrozenInstanceError):
        mist.count = 0  # ty: ignore[invalid-assignment]
