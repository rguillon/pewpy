"""The presets of `levels/sceneries.yaml`, and resolving a level's scenery from its preset."""

from functools import cache
from typing import Any

from pewpy.data import data_folder, read_yaml
from pewpy.scenery.params.checks import check_generators
from pewpy.scenery.params.reader import build, merge
from pewpy.scenery.params.scenery import SceneryParams
from pewpy.scenery.params.types import SceneryError


@cache
def presets() -> dict[str, Any]:
    """Read `levels/sceneries.yaml`: "default" and the presets."""
    return read_yaml(data_folder().joinpath("levels").joinpath("sceneries.yaml"))


def backgrounds() -> tuple[str, ...]:
    """Return the presets' names, in the file's order."""
    return tuple(name for name in presets() if name != "default")


def resolve(background: str, overrides: dict[str, Any] | None = None) -> SceneryParams:
    """Return the parameters of preset `background` with a level's `overrides`, checked (SceneryError if wrong)."""
    data = presets()
    if background not in data or background == "default":
        raise SceneryError("", f"unknown background {background!r}, expected one of {sorted(backgrounds())}")  # noqa: EM101 - the error builds its message
    merged = merge(merge(data["default"], data[background]), overrides or {})
    params = build(SceneryParams, merged, background, given={"name": background})
    check_generators(params)
    return params
