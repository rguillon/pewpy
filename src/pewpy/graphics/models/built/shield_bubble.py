"""The Shield Carrier's shield."""

from panda3d.core import NodePath, TransparencyAttrib, Vec3

from pewpy.graphics.models.mesh.builder import MeshBuilder


def shield_bubble_model() -> NodePath:
    """See-through sphere drawn around a Shield Carrier while its shield is up."""
    mesh = MeshBuilder()
    mesh.ellipsoid(Vec3(0, 0, 0), Vec3(0.62, 0.62, 0.62), (0.55, 0.85, 1.0, 0.3), rings=6, segments=12)
    bubble = NodePath(mesh.build("shield"))
    bubble.setTransparency(TransparencyAttrib.MAlpha)
    bubble.setDepthWrite(False)
    bubble.setLightOff()
    bubble.setShaderOff()
    return bubble
