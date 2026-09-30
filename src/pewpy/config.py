"""Tunable game constants.

Values marked "placeholder" are not decided in the specs yet; see docs/specs/decisions.md.
"""

# Window (placeholder: 3:4 portrait window)
WINDOW_TITLE = "pewpy"
WINDOW_WIDTH = 675
WINDOW_HEIGHT = 900

# 3D camera: sits in front of the play area, tilted so the top of the screen is farther away
CAMERA_FOV = 40.0  # vertical field of view, degrees
CAMERA_TILT = 25.0  # degrees; 0 looks straight at the play area

# Play area in world units, centered on the origin (placeholder: 3:4 portrait, vertical scroller)
PLAY_WIDTH = 1.5
PLAY_HEIGHT = 2.0

# Player ship (01-gameplay.md)
PLAYER_SPEED = 1.0  # world units per second
PLAYER_RESPONSIVENESS = 12.0  # how fast velocity reaches target speed (1/s); lower = more inertia
PLAYER_WIDTH = 0.12  # placeholder size; the full ship is the hitbox
PLAYER_HEIGHT = 0.12
PLAYER_START_Y = -0.75
PLAYER_LIVES = 5
PLAYER_HEALTH = 5.0  # placeholder: health bar size, one bar per life
PLAYER_INVULNERABILITY_TIME = 1.0  # seconds

# Player weapons: per-weapon values are in weapons.py (01-gameplay.md)

# Pickups (01-gameplay.md)
PICKUP_SIZE = 0.08
PICKUP_SPEED = 0.25  # drifting down, world units per second
PICKUP_UPGRADE_SHARE = 0.7  # when an enemy drops something: 70% upgrade capsule, 30% repair
REPAIR_AMOUNT = 2.0
MAX_LEVEL_UPGRADE_POINTS = 500

# Enemies: per-type values are in enemies.py (02-enemies.md)
ENEMY_BULLET_SIZE = 0.03
ENEMY_BULLET_DAMAGE = 1.0
ENEMY_RAM_DAMAGE = 2.0  # damage to the player when an enemy collides with the ship

# Model look (placeholder until 05-visuals.md is decided): see lighting.py
SHININESS = 24.0  # size of the specular highlights: higher = smaller, sharper
SPECULAR = 0.5  # strength of the specular highlights
REFLECTIVITY = 0.2  # how much faces facing the camera reflect the environment; edges always reflect more
BEVEL_WIDTH = 0.18  # rounded rim around each voxel face, as a fraction of the face
BEVEL_STRENGTH = 1.2  # how far the rim bends the light: 0 = flat, sharp cubes

# Background starfield (placeholder until 05-visuals.md is decided)
STAR_COUNT = 90
