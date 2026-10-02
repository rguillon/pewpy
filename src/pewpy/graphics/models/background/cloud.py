"""Glowing clouds (nebulas)."""

import math
import random

from panda3d.core import CardMaker, ColorBlendAttrib, NodePath, PNMImage, Texture

from pewpy.graphics.models.types import Color


def cloud_model(color: Color, seed: int = 0) -> NodePath:
    """Make a soft, lumpy glow on a 1 x 1 card, added to what's behind it (unlit, see-through)."""
    size = 64
    rng = random.Random(seed)
    blobs = [(rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7), rng.uniform(0.12, 0.25)) for _ in range(5)]
    image = PNMImage(size, size)
    for y in range(size):
        for x in range(size):
            u, v = (x + 0.5) / size, (y + 0.5) / size
            glow = sum(math.exp(-((u - bx) ** 2 + (v - by) ** 2) / (2 * r * r)) for bx, by, r in blobs) / 2.5
            edge = max(0.0, 1 - 2 * math.hypot(u - 0.5, v - 0.5)) ** 0.5  # nothing at the card's edges
            value = min(glow * edge, 1.0)
            image.setXel(x, y, color[0] * value, color[1] * value, color[2] * value)
    texture = Texture("cloud")
    texture.load(image)
    card = CardMaker("cloud")
    card.setFrame(-0.5, 0.5, -0.5, 0.5)
    cloud = NodePath(card.generate())
    cloud.setTexture(texture)
    cloud.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
    cloud.setDepthWrite(False)
    cloud.setLightOff()
    cloud.setShaderOff()
    return cloud
