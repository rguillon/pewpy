"""A gun's state: what it counts down to its next shot."""

from dataclasses import dataclass

from pewpy.game.weapons.guns.gun import Gun


@dataclass
class GunState:
    """Where a gun is at: its wait, its volley, its turn, its charge."""

    cooldown: float
    volley_left: int = 0
    volley_timer: float = 0.0
    volley_index: int = 0  # the next shot's place in its volley
    turned: float = 0.0
    charge: float = 0.0  # a laser: seconds until its beams fire (its warning beams show meanwhile)
    charging: float = 0.0  # a gun with `charge`: seconds until it fires
    beaming: float = 0.0  # a "beam" gun: seconds until its beam ends
    shots: int = 0  # volleys started: the sequence goes round with it
    volleys: int = 0  # volleys fired in full
    fired: bool = False  # an `at` gun
    item: Gun | None = None  # the pattern of the volley under way

    @property
    def busy(self) -> bool:
        """Charging, beaming or in the middle of a volley."""
        return self.volley_left > 0 or self.charging > 0 or self.beaming > 0
