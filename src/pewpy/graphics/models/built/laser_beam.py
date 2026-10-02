"""A laser's bright core."""

from panda3d.core import NodePath, TransparencyAttrib, Vec3

from pewpy.graphics.models.mesh.builder import MeshBuilder
from pewpy.graphics.models.types import Color


def laser_beam_model(color: Color = (0.85, 1.0, 1.0, 0.95)) -> NodePath:
    """A laser's bright core: a thin box, stretched to the beam's size (a 1 x 1 beam). The rest of the beam is
    light: streaks shooting along it (effects/laser.py) in a soft halo (effects/view.py).
    """
    mesh = MeshBuilder()
    mesh.box(Vec3(0, 0, 0), Vec3(0.25, 0.25, 1.0), color)
    beam = NodePath(mesh.build("laser"))
    beam.setTransparency(TransparencyAttrib.MAlpha)
    beam.setLightOff()
    beam.setShaderOff()
    return beam
