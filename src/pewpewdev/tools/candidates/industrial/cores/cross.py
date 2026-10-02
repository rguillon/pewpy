"""The cross core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_cross(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    arm = rng.uniform(0.35, 0.6) * cv.h
    cv.rect(mx - max(1, half // 3), mx + max(1, half // 3), 0, cv.h - 1, "h")
    cv.rect(mx - half, mx + half, arm - 1.5, arm + 1.5, "h")
