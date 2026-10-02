"""Things drifting down the background, layer by layer: clouds, planets, asteroids, mist (see layers/)."""

import random
from dataclasses import dataclass, field

from pewpy.scenery.ground.terrain import Area


@dataclass(eq=False)
class Drifter:
    """Something sliding down the background: a cloud, a planet, an asteroid. `angle` is (heading, pitch, roll)."""

    x: float
    y: float
    size: float
    speed_factor: float
    shape: int = 0
    spin: tuple[float, float, float] = (0.0, 0.0, 0.0)  # degrees per second
    angle: tuple[float, float, float] = (0.0, 0.0, 0.0)
    wind: float = 0.0  # sideways speed, world units per second


@dataclass(eq=False)
class DriftLayer:
    """Drifters at one depth. One that leaves the bottom comes back above the top, somewhere else."""

    kind: str  # "cloud", "planet", "rock" or "mist": what view.py draws
    depth: float
    area: Area
    drifters: list[Drifter]
    rng: random.Random = field(default_factory=random.Random)

    def update(self, dt: float, scroll_speed: float) -> None:
        """Scroll the drifters down and turn them; one that leaves at the bottom comes back at the top."""
        for drifter in self.drifters:
            drifter.y -= scroll_speed * drifter.speed_factor * dt
            (heading, pitch, roll), (spin_h, spin_p, spin_r) = drifter.angle, drifter.spin
            drifter.angle = (heading + spin_h * dt, pitch + spin_p * dt, roll + spin_r * dt)
            if drifter.y < self.area.bottom - drifter.size:
                drifter.y += self.area.height + 2 * drifter.size
                drifter.x = self.rng.uniform(self.area.left, self.area.right)
            drifter.x += drifter.wind * dt  # blown sideways: gone off one side, it comes back on the other
            if drifter.x > self.area.right + drifter.size:
                drifter.x -= self.area.width + 2 * drifter.size
            elif drifter.x < self.area.left - drifter.size:
                drifter.x += self.area.width + 2 * drifter.size
