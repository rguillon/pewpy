"""The props standing on the grounds (grounds/: the settlements, floras and outposts).

Buildings, farms, refinery units, trees, hangars, radars, domes...

Each prop is described in data/models/props/<name>.json: its kind, the box it was drawn in, and its parts with their
geometry and colors (see model.py). The grounds ask for a kind; a kind with several files picks one by the prop's
seed, stretched to the prop's lot. They're built in bulk with numpy as plain arrays (mesh.py); the ground's shader/
turns them into Panda3D geometry. Every vertex has 14 floats: position (3), normal (3), color (red, green, blue,
material) and texture data (4: along the wall, up the wall, the prop's seed from 0 to 1, unused). The material tells
the prop shader how to paint a face; the wall coordinates, in world units, place the windows.

Props are built in ground coordinates (x right, y down the loop, z up towards the camera), then turned into a
strip's model space (x right, y away from the camera, z up the screen) by `strip_arrays`. Independent from Panda3D.
"""

from pewpy.scenery.ground.props.mesh import SUNK, FloatArray, IndexArray, PropMesh
from pewpy.scenery.ground.props.model import PropModel, catalog
from pewpy.scenery.ground.settlement import Prop

__all__ = ["SUNK", "PropMesh", "PropModel", "build", "catalog", "strip_arrays"]


def build(mesh: PropMesh, prop: Prop) -> None:
    """Add a prop to a mesh: one of its kind's, picked by its seed."""
    models = catalog()[prop.kind]
    models[prop.seed % len(models)].build(mesh, prop)


def strip_arrays(props: list[Prop], first_y: float) -> tuple[FloatArray, IndexArray]:
    """Build every prop of a strip, in the strip's model space.

    x right, y away from the camera (heights towards the camera are -y), z up the screen from the strip's top edge
    (`first_y` down the loop).
    """
    mesh = PropMesh()
    for prop in props:
        build(mesh, prop)
    vertices, indices = mesh.arrays()
    model = vertices.copy()
    model[:, 1] = -vertices[:, 2]
    model[:, 2] = -(vertices[:, 1] - first_y)
    model[:, 4] = -vertices[:, 5]
    model[:, 5] = -vertices[:, 4]
    return model, indices
