"""Tunable game constants.

Values marked "placeholder" are not decided in the specs yet; see docs/specs/decisions.md.
"""

# Window (the user's choice: 1280 x 1024, a 5:4 landscape window)
WINDOW_TITLE = "pewpy"
SHOW_FPS = True  # frames per second in the top-right corner, on every screen
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 1024

# Sound (placeholders until 04-ui-audio.md is decided): see audio/
SFX_VOLUME = 0.8  # 0 to 1
MUSIC_VOLUME = 0.6
MUSIC_ON = True  # the M key turns the music on and off

# 3D camera: sits in front of the play area, tilted so the top of the screen is farther away
CAMERA_FOV = 40.0  # vertical field of view, degrees
CAMERA_TILT = 25.0  # degrees; 0 looks straight at the play area

# Play area in world units, centered on the origin: the window's shape (5:4), a vertical scroller. It was 1.5 wide
# (3:4 portrait) until the window became 1280 x 1024: the height, and with it the enemies' speeds, stop heights and
# timings, stayed the same; what goes across the screen was widened by WIDTH_SCALE (levels' x, crossing speeds...).
PLAY_WIDTH = 2.5
PLAY_HEIGHT = 2.0
WIDTH_SCALE = PLAY_WIDTH / 1.5

# Player ship (01-gameplay.md)
PLAYER_RESPONSIVENESS = 12.0  # how fast velocity reaches target speed (1/s); lower = more inertia
PLAYER_START_Y = -0.75
PLAYER_LIVES = 5
PLAYER_INVULNERABILITY_TIME = 1.0  # seconds

# Player weapons: per-weapon values are in weapons.py (01-gameplay.md)

# Pickups (01-gameplay.md)
PICKUP_SIZE = 0.08
PICKUP_SPEED = 0.25  # drifting down, world units per second
PICKUP_UPGRADE_SHARE = 0.7  # when an enemy drops something: 70% upgrade capsule...
PICKUP_LIFE_SHARE = 0.04  # ...4% extra life, the rest (26%) repair (placeholder, see decisions.md)
MAX_LIVES = 9  # an extra life beyond this gives EXTRA_LIFE_POINTS instead
EXTRA_LIFE_POINTS = 1000
REPAIR_AMOUNT = 2.0
BOSS_BEATEN_TIME = 3.0  # seconds of play after the boss is destroyed, to pick up what it dropped
MAX_LEVEL_UPGRADE_POINTS = 500

# Enemies: per-type values are in enemies.py (02-enemies.md)
ENEMY_BULLET_SIZE = 0.03
ENEMY_BULLET_DAMAGE = 1.0
ENEMY_RAM_DAMAGE = 2.0  # damage to the player when an enemy collides with the ship

# Every voxel model is built with cubes of this size, the Swarmer's (its 0.06 hitbox over its 9 columns): a
# model's size comes from its drawing (see models.py), which should about match its hitbox.
MODEL_VOXEL = 0.06 / 9

# Model look (placeholder until 05-visuals.md is decided): see lighting.py
SHININESS = 24.0  # size of the specular highlights: higher = smaller, sharper
SPECULAR = 0.5  # strength of the specular highlights
REFLECTIVITY = 0.2  # how much faces facing the camera reflect the environment; edges always reflect more
BEVEL_WIDTH = 0.18  # rounded rim around each voxel face, as a fraction of the face
BEVEL_STRENGTH = 1.2  # how far the rim bends the light: 0 = flat, sharp cubes

# Background starfield (placeholder until 05-visuals.md is decided)
STAR_COUNT = 90
