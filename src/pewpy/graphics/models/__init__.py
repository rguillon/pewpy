"""Procedural 3D models (placeholders until 05-visuals.md is decided).

Ships are voxel models, like pixel art extruded into blocks: each one is drawn as rows of characters, and a
palette gives every character a color and a thickness (in voxels, centered on the ship's depth), so the hull,
cockpit and wings stand out at different depths. The drawings are JSON files in `data/models/`, in one of
several forms (drawings/); mesh/ turns them into meshes, drawn.py into models (flames.py adds their engine flames).
The shapes that aren't drawings are built in code, each in its own module: built/ (turrets, pickups, shields,
lasers...) and background/ (asteroids, planets, clouds, mist).

Model space: X is right, Z is up the screen, Y is depth (negative Y faces the camera, so it is the "top"
of a ship). Drawn models are in world units: every cube is config.MODEL_VOXEL (the same on every ship), the
middle of the drawing at the origin. Other shapes (shield bubble, laser, cube) fit in a 1 x 1 x 1 box and are
stretched to their size.
The player points up the screen (+Z); enemies point down (-Z). The first row of a drawing is the top of the screen.
"""

from pewpy.graphics.models.background.cloud import cloud_model
from pewpy.graphics.models.background.distant_planet import distant_planet_model
from pewpy.graphics.models.background.mist import MIST_TEXTURES, mist_model
from pewpy.graphics.models.background.rock import rock_model
from pewpy.graphics.models.built.cube import make_cube
from pewpy.graphics.models.built.gun_turret import gun_turret_model
from pewpy.graphics.models.built.laser_beam import laser_beam_model
from pewpy.graphics.models.built.lightning_coil import lightning_coil_model
from pewpy.graphics.models.built.pickups import extra_life_model, pickup_model, repair_model
from pewpy.graphics.models.built.shield_bubble import shield_bubble_model
from pewpy.graphics.models.built.tank import tank_model
from pewpy.graphics.models.built.turret import turret_model
from pewpy.graphics.models.colors import METAL, main_colors, mottle, shade, tint
from pewpy.graphics.models.drawings.engines import (
    ENGINE_KEYS,
    FLAME_COLOR,
    FLAME_DIRECTIONS,
    OPTIONAL_ENGINE_KEYS,
    Engine,
    parse_engines,
)
from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.files import (
    DRAWINGS_FOLDER,
    load_drawing,
    load_engines,
    load_voxels,
    parse_voxels,
)
from pewpy.graphics.models.drawings.flat import DRAWING_KEYS, PALETTE_KEYS, parse_drawing
from pewpy.graphics.models.drawings.layered import LAYERED_KEYS
from pewpy.graphics.models.drawings.magica import VOX_KEYS, voxels_from_vox, voxels_to_vox
from pewpy.graphics.models.drawings.voxels import EMPTY, OPTIONAL_DRAWING_KEYS, Voxels, thickest, voxel_cells
from pewpy.graphics.models.drawn import BUILT_MODELS, drawing_model, model, voxel_model
from pewpy.graphics.models.facing import facing_roll
from pewpy.graphics.models.flames import FLAME_CORE_COLOR, FLAME_CORE_SIZE, FLAME_TEXTURE_SIZE, add_flame
from pewpy.graphics.models.mesh.builder import (
    BURN_UVS,
    GLOW_UVS,
    NO_BEVEL,
    QUAD_UVS,
    WATER_UV,
    MeshBuilder,
)
from pewpy.graphics.models.mesh.voxel_faces import (
    FACE_CORNERS,
    FACE_DIRECTIONS,
    OCCLUSION_BRIGHTNESS,
    face_axes,
    merged_faces,
    occlusion_level,
)
from pewpy.graphics.models.types import (
    UV,
    BoolArray,
    Cell,
    Color,
    Direction,
    FloatArray,
    IntArray,
    Outline,
    Palette,
    Vertex,
)

__all__ = [
    "BUILT_MODELS",
    "BURN_UVS",
    "DRAWINGS_FOLDER",
    "DRAWING_KEYS",
    "EMPTY",
    "ENGINE_KEYS",
    "FACE_CORNERS",
    "FACE_DIRECTIONS",
    "FLAME_COLOR",
    "FLAME_CORE_COLOR",
    "FLAME_CORE_SIZE",
    "FLAME_DIRECTIONS",
    "FLAME_TEXTURE_SIZE",
    "GLOW_UVS",
    "LAYERED_KEYS",
    "METAL",
    "MIST_TEXTURES",
    "NO_BEVEL",
    "OCCLUSION_BRIGHTNESS",
    "OPTIONAL_DRAWING_KEYS",
    "OPTIONAL_ENGINE_KEYS",
    "PALETTE_KEYS",
    "QUAD_UVS",
    "UV",
    "VOX_KEYS",
    "WATER_UV",
    "BoolArray",
    "Cell",
    "Color",
    "Direction",
    "Engine",
    "FloatArray",
    "IntArray",
    "MeshBuilder",
    "Outline",
    "Palette",
    "Vertex",
    "VoxelDrawingError",
    "Voxels",
    "add_flame",
    "cloud_model",
    "distant_planet_model",
    "drawing_model",
    "extra_life_model",
    "face_axes",
    "facing_roll",
    "gun_turret_model",
    "laser_beam_model",
    "lightning_coil_model",
    "load_drawing",
    "load_engines",
    "load_voxels",
    "main_colors",
    "make_cube",
    "merged_faces",
    "mist_model",
    "model",
    "mottle",
    "occlusion_level",
    "parse_drawing",
    "parse_engines",
    "parse_voxels",
    "pickup_model",
    "repair_model",
    "rock_model",
    "shade",
    "shield_bubble_model",
    "tank_model",
    "thickest",
    "tint",
    "turret_model",
    "voxel_cells",
    "voxel_model",
    "voxels_from_vox",
    "voxels_to_vox",
]
