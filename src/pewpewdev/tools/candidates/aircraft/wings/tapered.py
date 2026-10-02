"""Tapered wings: swept back, forward, or straight."""

from collections.abc import Callable

from pewpewdev.tools.candidates.canvas import Point, Rng


def tapered(
    sweep_range: tuple[float, float], chord_range: tuple[float, float]
) -> Callable[[Rng, int, float, float], list[Point]]:
    """Plan a wing tapering to its tip, swept back (positive) or forward (negative)."""

    def plan(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
        chord = height * rng.uniform(*chord_range)
        tip_chord = max(1.0, chord * rng.uniform(0.25, 0.5))
        tip_front = front - (root_x + 0.5) * rng.uniform(*sweep_range)
        return [(root_x, front), (-0.5, tip_front), (-0.5, tip_front - tip_chord), (root_x, front - chord)]

    return plan
