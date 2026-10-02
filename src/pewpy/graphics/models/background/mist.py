"""Mist."""

import math
import random

from panda3d.core import CardMaker, NodePath, PNMImage, Texture, TransparencyAttrib

MIST_TEXTURES = 4  # different cloud shapes, built once and shared
_mist_textures: dict[int, Texture] = {}


def mist_model(shape: int) -> NodePath:
    """A soft, lumpy, see-through cloud on a 1 x 1 card, white: color it with setColor (alpha: how see-through)."""
    shape %= MIST_TEXTURES
    if shape not in _mist_textures:
        size = 64
        rng = random.Random(100 + shape)  # noqa: S311 - visual randomness, not cryptography
        blobs = [(rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7), rng.uniform(0.1, 0.22)) for _ in range(7)]
        image = PNMImage(size, size, 4)
        for y in range(size):
            for x in range(size):
                u, v = (x + 0.5) / size, (y + 0.5) / size
                puff = sum(math.exp(-((u - bx) ** 2 + (v - by) ** 2) / (2 * r * r)) for bx, by, r in blobs) / 2.2
                edge = max(0.0, 1 - 2 * math.hypot(u - 0.5, v - 0.5)) ** 0.6  # nothing at the card's edges
                image.setXelA(x, y, 1.0, 1.0, 1.0, min(puff * edge, 1.0))
        texture = Texture(f"mist_{shape}")
        texture.load(image)
        _mist_textures[shape] = texture
    card = CardMaker("mist")
    card.setFrame(-0.5, 0.5, -0.5, 0.5)
    mist = NodePath(card.generate())
    mist.setTexture(_mist_textures[shape])
    mist.setTransparency(TransparencyAttrib.MAlpha)
    mist.setDepthWrite(False)
    mist.setTwoSided(True)
    mist.setLightOff()
    mist.setShaderOff()
    return mist
