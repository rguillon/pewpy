"""Secondary weapons from 01-gameplay.md: a machine-gun turret or a lightning gun, picked up from enemy drops.

They fire on their own, next to the selected weapon. The ship carries one at most, and a hit takes it away instead
of health. Independent from rendering.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

from pewpy.game.entities import Bullet, Entity

SECONDARY_WEAPONS = ("turret", "lightning")
SECONDARY_LETTERS = {"turret": "T", "lightning": "Z"}

# Turret: a little machine gun on the ship, shooting at the nearest enemy on screen (placeholder)
TURRET_FIRE_RATE = 5.0  # shots per second
TURRET_DAMAGE = 0.6
TURRET_BULLET_SPEED = 2.5
TURRET_BULLET_SIZE = 0.025

# Lightning gun: strikes the nearest enemy in range, then jumps from enemy to enemy (placeholder)
LIGHTNING_INTERVAL = 0.6  # seconds between two strikes
LIGHTNING_DAMAGE = 2.0  # to each enemy struck
LIGHTNING_RANGE = 0.7  # from the ship to the first enemy
LIGHTNING_JUMP = 0.35  # from one enemy to the next
LIGHTNING_CHAIN = 4  # enemies struck at most, the first one included
LIGHTNING_FLASH = 0.12  # seconds a bolt stays on screen

T = TypeVar("T", bound=Entity)


@dataclass
class SecondaryWeapon:
    """The secondary weapon the ship carries: "turret" or "lightning"."""

    kind: str
    cooldown: float = 0.0
    aim_x: float = 0.0  # where the turret points (a direction), for the drawing
    aim_y: float = 1.0

    def fire(self, dt: float, ship: Entity, targets: Sequence[T]) -> tuple[list[Bullet], list[T]]:
        """(turret bullets, enemies struck by lightning) this frame. It only fires when it has a target, at once
        when one comes after a wait.
        """
        self.cooldown = max(self.cooldown - dt, 0.0)
        if self.cooldown > 0:
            return [], []
        if self.kind == "turret":
            return self._turret(ship, targets), []
        return [], self._lightning(ship, targets)

    def _turret(self, ship: Entity, targets: Sequence[Entity]) -> list[Bullet]:
        target = _nearest(ship, targets)
        if target is None:
            return []
        distance = math.hypot(target.x - ship.x, target.y - ship.y) or 1.0
        self.aim_x, self.aim_y = (target.x - ship.x) / distance, (target.y - ship.y) / distance
        self.cooldown += 1.0 / TURRET_FIRE_RATE
        return [
            Bullet(
                x=ship.x,
                y=ship.y,
                vx=self.aim_x * TURRET_BULLET_SPEED,
                vy=self.aim_y * TURRET_BULLET_SPEED,
                width=TURRET_BULLET_SIZE,
                height=TURRET_BULLET_SIZE,
                damage=TURRET_DAMAGE,
            )
        ]

    def _lightning(self, ship: Entity, targets: Sequence[T]) -> list[T]:
        """The chain of enemies struck: the nearest in range of the ship, then each time the nearest one not struck
        yet within a jump of the last.
        """
        chain: list[T] = []
        here, reach = ship, LIGHTNING_RANGE
        while len(chain) < LIGHTNING_CHAIN:
            left = [target for target in targets if target not in chain]
            target = _nearest(here, left, reach)
            if target is None:
                break
            chain.append(target)
            here, reach = target, LIGHTNING_JUMP
        if chain:
            self.cooldown += LIGHTNING_INTERVAL
        return chain


def _nearest(origin: Entity, targets: Sequence[T], reach: float = math.inf) -> T | None:
    distance = {id(target): math.hypot(target.x - origin.x, target.y - origin.y) for target in targets}
    near = [target for target in targets if distance[id(target)] <= reach]
    return min(near, key=lambda target: distance[id(target)], default=None)
