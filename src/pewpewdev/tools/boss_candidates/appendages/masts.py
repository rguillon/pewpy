"""The masts appendage."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def masts(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    for _ in range(rng.randint(1, 3)):
        cv.line(
            mx - half * rng.uniform(0.2, 0.6),
            rng.uniform(0.2, 0.6) * cv.h,
            rng.uniform(0, mx - half),
            rng.uniform(0, cv.h * 0.3),
            "r",
            side,
        )
