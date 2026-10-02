"""The player's weapons from 01-gameplay.md: bullets, laser and missiles, with their levels.

They are in `data/weapons/player.json` (each level is a gun, see pewpy.game.weapons.guns). Independent from rendering.
"""

import json
from dataclasses import dataclass, field

from pewpy.data import data_folder
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet
from pewpy.game.weapons.guns import Gun, GunState, Shooter, parse_gun, step
from pewpy.game.weapons.player.secondary import SecondaryWeapon

_WEAPONS = json.loads((data_folder() / "weapons" / "player.json").read_text())
WEAPONS = tuple(_WEAPONS)  # the order the ship switches through them
LETTERS: dict[str, str] = {weapon: data["letter"] for weapon, data in _WEAPONS.items()}  # on the upgrade capsules
LEVELS: dict[str, tuple[Gun, ...]] = {
    weapon: tuple(parse_gun(level) for level in data["levels"]) for weapon, data in _WEAPONS.items()
}
MAX_LEVEL = len(LEVELS[WEAPONS[0]])  # every weapon has as many levels


@dataclass(frozen=True)
class Beam:
    """The laser as drawn this frame: from `bottom` to `top`, centered on `x`."""

    x: float
    bottom: float
    top: float
    width: float


@dataclass
class Arsenal:
    """The weapons the ship carries, their levels, which one is selected, and the secondary weapon if it has one.

    See secondary.py. They share one wait between shots (`cooldown`).
    """

    levels: dict[str, int] = field(default_factory=lambda: dict.fromkeys(WEAPONS, 1))
    selected: str = WEAPONS[0]
    cooldown: float = 0.0
    secondary: SecondaryWeapon | None = None
    states: dict[str, GunState] = field(default_factory=dict)  # each weapon's (missiles take turns from side to side)

    @property
    def level(self) -> int:
        """The selected weapon's level."""
        return self.levels[self.selected]

    @property
    def gun(self) -> Gun:
        """The selected weapon at its level."""
        return LEVELS[self.selected][self.level - 1]

    def switch(self) -> None:
        """Select the next weapon."""
        self.selected = WEAPONS[(WEAPONS.index(self.selected) + 1) % len(WEAPONS)]

    def upgrade(self, weapon: str) -> bool:
        """Raise `weapon` by one level; False if it was already at the maximum."""
        if self.levels[weapon] >= MAX_LEVEL:
            return False
        self.levels[weapon] += 1
        return True

    def laser(self, firing: bool) -> Gun | None:
        """Return the laser ("ray") while it is selected and firing, else None."""
        return self.gun if firing and self.gun.pattern == "ray" else None

    def fire(self, dt: float, firing: bool, ship: Entity) -> list[Bullet]:
        """Bullets or missiles shot this frame (the laser is handled by the world, it needs the enemies)."""
        gun = self.gun
        state = self.states.setdefault(self.selected, GunState(cooldown=0.0))
        state.cooldown = self.cooldown
        trigger = firing and gun.pattern != "ray"
        shots = step(gun, state, Shooter(ship, None, hostile=False, forward=1, trigger=trigger), dt)
        self.cooldown = state.cooldown
        return [shot for shot in shots if isinstance(shot, Bullet)]
