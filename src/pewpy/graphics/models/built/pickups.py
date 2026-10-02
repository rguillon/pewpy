"""What the enemies drop: capsules, repairs and extra lives."""

from panda3d.core import NodePath, TextNode

from pewpy import config
from pewpy.graphics.models.colors import tint
from pewpy.graphics.models.drawings.files import load_drawing
from pewpy.graphics.models.drawn import drawing_model, voxel_model
from pewpy.graphics.models.types import Color


def pickup_model(letter: str, color: Color) -> NodePath:
    """Make a blocky colored capsule with a letter that always faces the camera.

    The capsule's drawing is in shades of grey, multiplied by the pickup's color.
    """
    rows, palette = load_drawing("capsule")
    tinted = {char: (tint(grey, color), height) for char, (grey, height) in palette.items()}
    model = voxel_model(f"pickup_{letter}", rows, tinted)
    extent = max(len(rows[0]), len(rows)) * config.MODEL_VOXEL
    text = TextNode("letter")
    text.setText(letter)
    text.setAlign(TextNode.ACenter)
    text.setTextColor(0.05, 0.05, 0.1, 1)
    label = model.attachNewNode(text)
    label.setScale(0.75 * extent)
    label.setPos(0, 0, -0.27 * extent)  # on the spin axis, so it stays centered while the capsule turns
    label.setBillboardPointEye()
    label.setLightOff()
    label.setShaderOff()
    # Drawn after everything else and without a depth test, so the capsule never hides it.
    label.setBin("fixed", 0)
    label.setDepthTest(False)
    label.setDepthWrite(False)
    return model


def repair_model() -> NodePath:
    """Make the repair pickup's model."""
    return drawing_model("repair")


def extra_life_model() -> NodePath:
    """Make the extra life's model."""
    return drawing_model("extra_life")
