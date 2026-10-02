"""The big wings appendage."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def big_wings(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    root, sweep = rng.uniform(0.3, 0.6) * cv.h, rng.uniform(-0.2, 0.3) * cv.h
    chord = rng.uniform(0.15, 0.3) * cv.h
    tip = max(2.0, chord * rng.uniform(0.2, 0.5))
    cv.polygon(
        [(mx - half * 0.5, root), (0, root - sweep), (0, root - sweep + tip), (mx - half * 0.5, root + chord)],
        "w",
        side,
    )
