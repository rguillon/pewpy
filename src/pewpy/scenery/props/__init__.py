"""The props standing on the grounds (settlement.py, landscapes.py): buildings, farms, refinery units, trees...

Each kind is built by its own module (`build(mesh, rng, prop, colors)`), from its seed: every kind has variants
(a tower with one or two setbacks, a hipped or gabled roof, a domed or floating-roof tank...), and colors that vary
a little around the scenery's (`props`, see params.py). They're built in bulk with numpy as plain arrays
(mesh.py); ground_shader.py turns them into Panda3D geometry. Every vertex has 14 floats: position (3), normal (3),
color (red, green, blue, material) and texture data (4: along the wall, up the wall, the prop's seed from 0 to 1,
unused). The material tells the prop shader how to paint a face; the wall coordinates, in world units, place the
windows.

Props are built in ground coordinates (x right, y down the loop, z up towards the camera), then turned into a
strip's model space (x right, y away from the camera, z up the screen) by `strip_arrays`. Independent from Panda3D.
"""

import random
from collections.abc import Callable

from pewpy.scenery.params import PropColors
from pewpy.scenery.props import (
    barn,
    building,
    cooling_tower,
    dead_tree,
    greenhouse,
    hedge,
    house,
    palm,
    pipes,
    plant,
    silo,
    stack,
    tank,
    tree,
)
from pewpy.scenery.props.mesh import SUNK, FloatArray, IndexArray, PropMesh
from pewpy.scenery.settlement import Prop

__all__ = ["BUILDERS", "SUNK", "PropMesh", "build", "strip_arrays"]

Builder = Callable[[PropMesh, random.Random, Prop, PropColors], None]
BUILDERS: dict[str, Builder] = {
    "building": building.build,
    "house": house.build,
    "barn": barn.build,
    "silo": silo.build,
    "greenhouse": greenhouse.build,
    "tank": tank.build,
    "plant": plant.build,
    "stack": stack.build,
    "pipes": pipes.build,
    "cooling_tower": cooling_tower.build,
    "tree": tree.build,
    "palm": palm.build,
    "dead_tree": dead_tree.build,
    "hedge": hedge.build,
}


def build(mesh: PropMesh, prop: Prop, colors: PropColors) -> None:
    """Add a prop to a mesh."""
    rng = random.Random(prop.seed)  # noqa: S311 - looks, not cryptography
    mesh.seed = (prop.seed % 997) / 997
    BUILDERS[prop.kind](mesh, rng, prop, colors)


def strip_arrays(props: list[Prop], first_y: float, colors: PropColors) -> tuple[FloatArray, IndexArray]:
    """Every prop of a strip, in the strip's model space: x right, y away from the camera (heights towards the
    camera are -y), z up the screen from the strip's top edge (`first_y` down the loop)."""
    mesh = PropMesh()
    for prop in props:
        build(mesh, prop, colors)
    vertices, indices = mesh.arrays()
    model = vertices.copy()
    model[:, 1] = -vertices[:, 2]
    model[:, 2] = -(vertices[:, 1] - first_y)
    model[:, 4] = -vertices[:, 5]
    model[:, 5] = -vertices[:, 4]
    return model, indices
