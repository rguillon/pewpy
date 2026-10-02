"""Checking the generators and painters a scenery names: they exist and get what they need."""

from collections.abc import Mapping
from typing import Protocol

from pewpy.scenery.params.colors import FLUID_COLORS, STYLE_COLORS, SURFACE_COLORS
from pewpy.scenery.params.scenery import SceneryParams
from pewpy.scenery.params.types import Color3, Knobs, SceneryError


def check_generators(params: SceneryParams) -> None:
    """Check the generators and painters named exist, and get the numbers and colors they need."""
    from pewpy.scenery.ground import kinds  # noqa: PLC0415 - the generators read the parameters: import cycle

    name = params.name
    if params.ground is not None:
        _check_knobs(params.ground.landscape, params.ground.shape, kinds.LANDSCAPES, f"{name}.ground.shape")
        _check_names(params.ground.style, params.ground.colors, STYLE_COLORS, f"{name}.ground.colors")
    if params.fluid is not None:
        _check_names(params.fluid.kind, params.fluid.colors, FLUID_COLORS, f"{name}.fluid.colors")
    if params.settlement is not None:
        _check_knobs(params.settlement.kind, params.settlement.layout, kinds.SETTLEMENTS, f"{name}.settlement.layout")
        _check_names(params.settlement.kind, params.settlement.colors, SURFACE_COLORS, f"{name}.settlement.colors")
    if params.flora is not None:
        _check_knobs(params.flora.kind, params.flora.knobs, kinds.FLORAS, f"{name}.flora.knobs")
    if params.outposts is not None:
        compounds = kinds.outposts.COMPOUNDS
        unknown = sorted(set(params.outposts.kinds) - set(compounds))
        if unknown or not params.outposts.kinds:
            raise SceneryError(f"{name}.outposts.kinds", f"unknown {unknown}, expected some of {sorted(compounds)}")  # noqa: EM102 - the error builds its message


class _Generator(Protocol):
    """A landscape, a flora or a settlement (grounds/): it names the numbers it needs."""

    @property
    def knobs(self) -> tuple[str, ...]: ...


def _check_knobs(kind: str, knobs: Knobs, generators: Mapping[str, _Generator], where: str) -> None:
    if kind not in generators:
        raise SceneryError(where, f"unknown {kind!r}, expected one of {sorted(generators)}")
    _exactly(set(knobs), set(generators[kind].knobs), where)


def _check_names(kind: str, colors: dict[str, Color3], names: dict[str, tuple[str, ...]], where: str) -> None:
    if kind not in names:
        raise SceneryError(where, f"unknown {kind!r}, expected one of {sorted(names)}")
    _exactly(set(colors), set(names[kind]), where)


def _exactly(given: set[str], needed: set[str], where: str) -> None:
    if given - needed:
        raise SceneryError(where, f"unknown {sorted(given - needed)}, expected {sorted(needed)}")
    if needed - given:
        raise SceneryError(where, f"missing {sorted(needed - given)}")
