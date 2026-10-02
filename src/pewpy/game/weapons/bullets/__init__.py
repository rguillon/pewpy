"""Every kind of shot (01-gameplay.md, 02-enemies.md "Enemy weapons"), each in its own module.

The plain bullet, the player's missiles, snaking, accelerating and curving shots, and laser beams. The guns fire
them (see pewpy.game.weapons.guns). Independent from rendering.
"""

from pewpy.game.weapons.bullets.accel import AccelBullet
from pewpy.game.weapons.bullets.beam import BEAM_BOTTOM, beam
from pewpy.game.weapons.bullets.boss_beam import BossBeam
from pewpy.game.weapons.bullets.bullet import Bullet
from pewpy.game.weapons.bullets.curve import CURVE_TIME, CurveBullet
from pewpy.game.weapons.bullets.missile import Missile
from pewpy.game.weapons.bullets.wave import WaveBullet

__all__ = [
    "BEAM_BOTTOM",
    "CURVE_TIME",
    "AccelBullet",
    "BossBeam",
    "Bullet",
    "CurveBullet",
    "Missile",
    "WaveBullet",
    "beam",
]
