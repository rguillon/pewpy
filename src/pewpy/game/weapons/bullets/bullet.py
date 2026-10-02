"""The plain bullet, which every other kind of shot is."""

from dataclasses import dataclass

from pewpy.game.entities import Entity


@dataclass(eq=False)
class Bullet(Entity):
    damage: float = 1.0
    hostile: bool = False  # True for enemy bullets
    style: str = "normal"  # how to draw it, e.g. "sniper" for the Sniper's shots
    life: float | None = None  # seconds before it vanishes by itself (a laser beam); None: until it leaves the screen
    pierces: bool = False  # True: goes on after hitting (a laser beam)
    harmless: bool = False  # True: only shows something coming (a laser's warning beam), never hits

    def move(self, dt: float) -> None:
        super().move(dt)
        if self.life is not None:
            self.life -= dt
            if self.life <= 0:
                self.alive = False
