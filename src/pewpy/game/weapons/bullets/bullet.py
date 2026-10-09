"""The plain bullet, which every other kind of shot is."""

import math
from dataclasses import dataclass

from pewpy.game.entities import Entity

SETTLE_SPEED = 0.5  # world units per second: how fast a shot fired above (or under) the play plane goes back to it


@dataclass(eq=False)
class Bullet(Entity):
    """A shot: how much it hurts, whose it is, how it's drawn, how long it lasts."""

    damage: float = 1.0
    hostile: bool = False  # True for enemy bullets
    style: str = "normal"  # how to draw it, e.g. "sniper" for the Sniper's shots
    life: float | None = None  # seconds before it vanishes by itself (a laser beam); None: until it leaves the screen
    pierces: bool = False  # True: goes on after hitting (a laser beam)
    harmless: bool = False  # True: only shows something coming (a laser's warning beam), never hits
    # Where it's drawn, from the play plane, away from the camera (negative: nearer it): it leaves its muzzle at the
    # muzzle's depth, then goes back to the plane at `settle` world units per second (0: it stays, like a beam).
    depth: float = 0.0
    settle: float = SETTLE_SPEED

    def move(self, dt: float) -> None:
        """Move, go back towards the play plane, and count down its life if it has one."""
        super().move(dt)
        step = self.settle * dt
        self.depth = 0.0 if abs(self.depth) <= step else self.depth - math.copysign(step, self.depth)
        if self.life is not None:
            self.life -= dt
            if self.life <= 0:
                self.alive = False
