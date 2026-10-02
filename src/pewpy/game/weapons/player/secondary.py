"""Secondary weapons from 01-gameplay.md: a machine-gun turret or a lightning gun, picked up from enemy drops, in
`data/weapons/secondary.json` (each is a gun, see pewpy.game.weapons.guns).

They fire on their own, next to the selected weapon, at the nearest enemy. The ship carries one at most, and a hit
takes it away instead of health. Independent from rendering.
"""

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TypeVar

from pewpy.data import data_folder
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet
from pewpy.game.weapons.guns import Gun, GunState, Shooter, chain, nearest, parse_gun, step

_SECONDARY = json.loads((data_folder() / "weapons" / "secondary.json").read_text())
SECONDARY_WEAPONS = tuple(_SECONDARY)
SECONDARY_LETTERS: dict[str, str] = {kind: data["letter"] for kind, data in _SECONDARY.items()}  # on the capsules
SECONDARY_GUNS: dict[str, Gun] = {kind: parse_gun(data["gun"]) for kind, data in _SECONDARY.items()}

T = TypeVar("T", bound=Entity)


@dataclass
class SecondaryWeapon:
    """The secondary weapon the ship carries: "turret" or "lightning"."""

    kind: str
    state: GunState = field(default_factory=lambda: GunState(cooldown=0.0))
    aim_x: float = 0.0  # where the turret points (a direction), for the drawing
    aim_y: float = 1.0

    @property
    def gun(self) -> Gun:
        return SECONDARY_GUNS[self.kind]

    def fire(self, dt: float, ship: Entity, targets: Sequence[T]) -> tuple[list[Bullet], list[T]]:
        """(bullets, enemies struck by a "chain" gun) this frame. It only fires when it has a target, at once when
        one comes after a wait.
        """
        gun = self.gun
        if gun.pattern == "chain":
            struck = chain(gun, ship, targets)
            target = struck[0] if struck else None
        else:
            struck, target = [], nearest(ship, targets)
        volleys = self.state.volleys
        shots = [shot for shot in step(gun, self.state, Shooter(ship, target, hostile=False, forward=1), dt)
                 if isinstance(shot, Bullet)]  # fmt: skip
        if self.state.volleys == volleys:
            return [], []
        if shots and target is not None:  # the turret turns to where it fired
            distance = math.hypot(target.x - ship.x, target.y - ship.y) or 1.0
            self.aim_x, self.aim_y = (target.x - ship.x) / distance, (target.y - ship.y) / distance
        return shots, struck
