"""A laser beam fired from a muzzle (a "beam" gun, like the Lancer's)."""

from pewpy import config
from pewpy.game.weapons.bullets.bullet import Bullet

BEAM_BOTTOM = -config.PLAY_HEIGHT / 2 - 0.1  # beams go down past the bottom of the screen


def beam(x: float, top: float, width: float, duration: float) -> Bullet:
    """Make a laser beam from `top` straight down past the bottom of the screen (like the Lancer's)."""
    return Bullet(
        x=x,
        y=(top + BEAM_BOTTOM) / 2,
        width=width,
        height=top - BEAM_BOTTOM,
        damage=config.ENEMY_BULLET_DAMAGE,
        hostile=True,
        style="beam",
        life=duration,
        pierces=True,
    )
