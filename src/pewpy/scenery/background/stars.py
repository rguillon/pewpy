"""Stars, in layers scrolling at different speeds."""

import random
from dataclasses import dataclass

from pewpy.scenery.ground.terrain import Area
from pewpy.scenery.params import Stars


@dataclass(eq=False)
class StarLayer:
    """Stars that scroll together. The layer is drawn twice, one copy above the other, and slides down by
    `offset` (wrapping every `area.height`), so it loops seamlessly without moving each star.
    """

    area: Area
    speed_factor: float
    size: float
    brightness: float
    stars: list[tuple[float, float]]  # (x, y) inside `area`, before scrolling
    offset: float = 0.0

    def update(self, dt: float, scroll_speed: float) -> None:
        self.offset = (self.offset + scroll_speed * self.speed_factor * dt) % self.area.height


class Starfield:
    def __init__(self, stars: Stars, area: Area, count: int | None = None, seed: int | None = None) -> None:
        """Stars over `area`; `count`: in all (default: the stars' count)."""
        rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        count = stars.count if count is None else count
        self.layers = [
            StarLayer(
                area,
                layer.speed,
                layer.size,
                layer.brightness,
                [
                    (rng.uniform(area.left, area.right), rng.uniform(area.bottom, area.top))
                    for _ in range(count // len(stars.layers))
                ],
            )
            for layer in stars.layers
        ]

    def update(self, dt: float, scroll_speed: float) -> None:
        for layer in self.layers:
            layer.update(dt, scroll_speed)
