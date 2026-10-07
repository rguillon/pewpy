"""The kit: hardcoded ship parts, placed together into ships (the enemies', and the player's).

Each family of parts in its own module: hulls.py (profiles stretched along the ship), wings.py (outlines), cockpits.py,
engines.py (nozzles and nacelles), weapons.py (barrels, gatlings, turrets, missiles, a side cannon) and extras.py (fins,
antennas, a radar dome, intakes, armor, a livery, markings). archetypes.py has the recipes choosing and placing them
(fighter, interceptor, bomber, drone, gunship, heavy; and the player's: vanguard, juggernaut, phantom); ship.py holds
the voxels and writes the 3D drawing.
"""

from pewpy.generators.models.ships.kit.archetypes import ARCHETYPES, PLAYER_ARCHETYPES
from pewpy.generators.models.ships.kit.ship import Ship

__all__ = ["ARCHETYPES", "PLAYER_ARCHETYPES", "Ship"]
