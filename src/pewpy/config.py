"""Tunable game constants: the window, the play area, the camera, the looks; and the game's rules.

The rules are read from `data/rules.yaml`. Values marked "placeholder" are not decided in the specs yet; they are
marked *(placeholder)* in docs/specs/.
"""

from pewpy.data import data_folder, read_yaml

# Window (the user's choice: 1280 x 1024, a 5:4 landscape window)
WINDOW_TITLE = "pewpy"
SHOW_FPS = True  # frames per second in the top-right corner, on every screen
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 1024
# The 3D scene is drawn at most this many pixels tall, then stretched over the game area (the HUD stays sharp):
# the ground's shader is painted per pixel, too slow on a 4K screen with a small GPU (placeholder).
SCENE_MAX_HEIGHT = 1440

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

# The game's rules (01-gameplay.md, 02-enemies.md): in `data/rules.yaml`
_RULES = read_yaml(data_folder() / "rules.yaml")
_PLAYER, _PICKUPS, _ENEMIES = _RULES["player"], _RULES["pickups"], _RULES["enemies"]

PLAYER_RESPONSIVENESS: float = _PLAYER[
    "responsiveness"
]  # how fast velocity reaches target speed (1/s): lower, more inertia
PLAYER_START_Y: float = _PLAYER["start_y"]
PLAYER_LIVES: int = _PLAYER["lives"]
PLAYER_INVULNERABILITY_TIME: float = _PLAYER["invulnerability_time"]  # seconds, after a hit
MAX_LIVES: int = _PLAYER["max_lives"]  # an extra life beyond this gives EXTRA_LIFE_POINTS instead
EXTRA_LIFE_POINTS: int = _PLAYER["extra_life_points"]

# Player weapons: in data/weapons/ (see game/weapons/)

PICKUP_SIZE: float = _PICKUPS["size"]
PICKUP_SPEED: float = _PICKUPS["speed"]  # drifting down, world units per second
PICKUP_UPGRADE_SHARE: float = _PICKUPS["upgrade_share"]  # when an enemy drops something: an upgrade capsule...
PICKUP_LIFE_SHARE: float = _PICKUPS["life_share"]  # ...an extra life...
PICKUP_SECONDARY_SHARE: float = _PICKUPS["secondary_share"]  # ...a secondary weapon, else a repair
REPAIR_AMOUNT: float = _PICKUPS["repair_amount"]
MAX_LEVEL_UPGRADE_POINTS: int = _PICKUPS["max_level_upgrade_points"]  # an upgrade for a weapon at its top level
BOSS_BEATEN_TIME: float = _RULES["bosses"]["beaten_time"]  # seconds of play after the final boss, to pick things up

# The level's start and end (placeholders): the ship flies in from the bottom, then away through the top
ARRIVAL_TIME = 1.5  # seconds from below the screen to its starting place, slowing down
DEPARTURE_ACCELERATION = 3.0  # world units per second squared, flying up once the level is over

# Enemies: each kind in data/enemies/ (see game/enemies/)
ENEMY_BULLET_SIZE: float = _ENEMIES["bullet_size"]
ENEMY_BULLET_DAMAGE: float = _ENEMIES["bullet_damage"]
ENEMY_RAM_DAMAGE: float = _ENEMIES["ram_damage"]  # damage to the player when an enemy collides with the ship

# Every voxel model is built with cubes of this size, the Swarmer's (its 0.06 hitbox over its 9 columns): a
# model's size comes from its drawing (see pewpy.graphics.models), which should about match its hitbox.
MODEL_VOXEL = 0.06 / 9

# Model look (placeholder until 05-visuals.md is decided): see lighting.py
SHININESS = 24.0  # size of the specular highlights: higher = smaller, sharper
SPECULAR = 0.5  # strength of the specular highlights
REFLECTIVITY = 0.2  # how much faces facing the camera reflect the environment; edges always reflect more
BEVEL_WIDTH = 0.18  # rounded rim around each voxel face, as a fraction of the face
BEVEL_STRENGTH = 1.2  # how far the rim bends the light: 0 = flat, sharp cubes

# Background starfield (placeholder until 05-visuals.md is decided)
STAR_COUNT = 90
