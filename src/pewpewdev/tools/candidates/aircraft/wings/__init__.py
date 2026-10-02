"""The aircraft's wing plans, each in its own module."""

from collections.abc import Callable

from pewpewdev.tools.candidates.aircraft.wings.cranked import cranked
from pewpewdev.tools.candidates.aircraft.wings.delta import delta
from pewpewdev.tools.candidates.aircraft.wings.ogival import ogival
from pewpewdev.tools.candidates.aircraft.wings.tapered import tapered
from pewpewdev.tools.candidates.canvas import Point, Rng

WING_PLANS: dict[str, Callable[[Rng, int, float, float], list[Point]]] = {
    "swept": tapered((0.4, 1.0), (0.22, 0.35)),
    "forward": tapered((-0.6, -0.3), (0.22, 0.35)),
    "straight": tapered((0.0, 0.15), (0.12, 0.2)),
    "delta": delta,
    "ogival": ogival,
    "cranked": cranked,
}
