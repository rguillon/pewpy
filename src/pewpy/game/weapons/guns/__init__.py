"""Guns (01-gameplay.md "Weapons", 02-enemies.md "Enemy weapons", 02-enemies-bosses.md).

How the player's weapons and every enemy and boss fire their bullets, launch their projectiles or fire their beams.
Independent from rendering.

A gun (Gun, gun.py) is data, read from the YAML files (the player's weapons in `data/weapons/`, the enemies' with
them, see pewpy.game.enemies.spec); its GunState (state.py) counts down to its next shot. `step` (timing/: each way of
timing the shots in its own module) runs a gun for a frame and returns what it fired (patterns.py): bullets of
several kinds (styles.py, see pewpy.game.weapons.bullets and Gun.style), enemies (launch.py: projectiles like
rockets and homing missiles, mines, Sparks...) or beams (laser.py). Two patterns aren't fired by `step`: "ray" (the
player's laser, which the world plays out against the enemies) and "chain" (the lightning gun, see chain.py).
"""

from pewpy.game.weapons.guns.chain import chain, nearest
from pewpy.game.weapons.guns.gun import Distance, Gun, distance, parse_gun
from pewpy.game.weapons.guns.laser import LASER_WARNING, WARNING_WIDTH, laser_beams
from pewpy.game.weapons.guns.launch import PROJECTILES
from pewpy.game.weapons.guns.patterns import SWEEP_PERIOD, fire, pattern_angles
from pewpy.game.weapons.guns.shooter import Maker, NoMakerError, Shooter
from pewpy.game.weapons.guns.state import GunState
from pewpy.game.weapons.guns.styles import ACCEL_START, ACCEL_TOP, BULLET_SIZES, HEAVY_BULLET_SIZE, styled_bullet
from pewpy.game.weapons.guns.timing import step

__all__ = [
    "ACCEL_START",
    "ACCEL_TOP",
    "BULLET_SIZES",
    "HEAVY_BULLET_SIZE",
    "LASER_WARNING",
    "PROJECTILES",
    "SWEEP_PERIOD",
    "WARNING_WIDTH",
    "Distance",
    "Gun",
    "GunState",
    "Maker",
    "NoMakerError",
    "Shooter",
    "chain",
    "distance",
    "fire",
    "laser_beams",
    "nearest",
    "parse_gun",
    "pattern_angles",
    "step",
    "styled_bullet",
]
