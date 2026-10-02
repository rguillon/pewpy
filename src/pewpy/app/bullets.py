"""How bullets look: balls of energy, colored by who fired them and their style."""

from pewpy.app.window import Color
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet, Missile
from pewpy.graphics.sprites import Sprite

PLAYER_BULLET_COLOR: Color = (0.3, 1.0, 0.25, 1)  # bright green
ENEMY_BULLET_COLOR: Color = (1.0, 0.5, 0.9, 1)
SNIPER_BULLET_COLOR: Color = (0.4, 0.6, 1.0, 1)
HEAVY_BULLET_COLOR: Color = (1.0, 0.55, 0.15, 1)  # big shots: bosses, Rocket Trucks
WAVE_BULLET_COLOR: Color = (0.75, 0.45, 1.0, 1)  # the Serpent's snaking shots
ACCEL_BULLET_COLOR: Color = (0.3, 0.95, 1.0, 1)  # bosses' shots speeding up
CURVE_BULLET_COLOR: Color = (1.0, 0.9, 0.3, 1)  # bosses' shots on bending paths
WARNING_BEAM_COLOR: Color = (1.0, 0.1, 0.1, 0.7)  # a laser about to fire: thin, harmless, red
BULLET_COLORS: dict[str, Color] = {
    "sniper": SNIPER_BULLET_COLOR,
    "heavy": HEAVY_BULLET_COLOR,
    "warning": WARNING_BEAM_COLOR,
    "wave": WAVE_BULLET_COLOR,
    "accel": ACCEL_BULLET_COLOR,
    "curve": CURVE_BULLET_COLOR,
}  # by Bullet.style; enemy shots of any other style (the Buckshot's pellets too) are pink
BULLET_GLOW = 3.2  # a bullet's sprite with its halo, compared with its hitbox
BULLET_BODY = 0.3  # how much of the sprite's radius is the ball itself (about the hitbox), the rest is its halo
WARNING_GLOW = 1.8  # a laser's warning, compared with the beam's width
MAX_BULLETS = 512


def is_round_bullet(entity: Entity) -> bool:
    """Tell whether an entity is drawn as a round bullet sprite (not a missile or a beam)."""
    return isinstance(entity, Bullet) and not isinstance(entity, Missile) and not is_beam(entity)


def is_beam(bullet: Entity) -> bool:
    """Tell whether a bullet is an enemy's laser beam (not its harmless warning): drawn like the player's laser."""
    return isinstance(bullet, Bullet) and bullet.hostile and bullet.style == "beam"


def bullet_sprite(bullet: Entity) -> Sprite:
    """Make a bullet's sprite: a ball of energy (an oval for the player's long bullets) in a halo.

    The ball is about the hitbox; a laser's warning is a soft line instead, its sides fading out.
    """
    if isinstance(bullet, Bullet) and bullet.hostile:
        color = BULLET_COLORS.get(bullet.style, ENEMY_BULLET_COLOR)
        if bullet.style == "warning":  # as long as the beam itself: only its sides fade out
            return Sprite(bullet.x, bullet.y, bullet.width * WARNING_GLOW, bullet.height, color)
    else:
        color = PLAYER_BULLET_COLOR
    phase = id(bullet) % 628 / 100  # the same for the bullet's whole flight
    return Sprite(
        bullet.x, bullet.y, bullet.width * BULLET_GLOW, bullet.height * BULLET_GLOW, color, energy=1.0, phase=phase
    )
