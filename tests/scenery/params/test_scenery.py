import dataclasses

import pytest

from pewpy.scenery.params.presets import resolve
from pewpy.scenery.params.scenery import SceneryParams


def test_a_scenery_is_its_sky_light_air_and_layers() -> None:
    scenery = resolve("space")
    assert isinstance(scenery, SceneryParams)
    assert {field.name for field in dataclasses.fields(SceneryParams)} >= {"name", "sky", "light", "ground", "stars"}
    assert len(scenery.sky) == 3


def test_a_scenery_cant_be_changed_once_read() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        resolve("space").sky = (0.0, 0.0, 0.0)  # ty: ignore[invalid-assignment]
