"""Engine flames: two crossed glowing cards at each engine's nozzle."""

from panda3d.core import CardMaker, ColorBlendAttrib, NodePath, PandaNode, PNMImage, Texture

from pewpy.graphics.models.drawings.engines import FLAME_DIRECTIONS, Engine
from pewpy.graphics.models.types import Color

FLAME_CORE_COLOR: Color = (0.95, 0.98, 1.0, 1)
FLAME_CORE_SIZE = (0.45, 0.5)  # the core's width and length, as a part of the flame's
FLAME_TEXTURE_SIZE = (32, 64)


def add_flame(model: NodePath, engine: Engine, shape: tuple[int, int], size: float) -> NodePath:
    """Add a flame under `model` at `engine`'s nozzle.

    `shape` is the model's (columns, rows) and `size` its voxel size. The flame's length is its Z scale: the game makes
    it flicker by changing it.
    """
    columns, rows = shape
    x = (engine.x - (columns - 1) / 2) * size
    edge = engine.y + (0.5 if engine.towards == "bottom" else -0.5)  # the side of the voxel the flame leaves from
    z = ((rows - 1) / 2 - edge) * size
    flame = model.attachNewNode("flame")
    flame.setPos(x, -engine.z * size, z)
    flame.setR(FLAME_DIRECTIONS[engine.towards])
    flame.setScale(engine.width * size, engine.width * size, engine.length * size)
    for part, color, scale in (("glow", engine.color, (1.0, 1.0)), ("core", FLAME_CORE_COLOR, FLAME_CORE_SIZE)):
        node = flame.attachNewNode(part)
        for heading in (0, 90):  # two crossed cards: it still looks like a flame when the ship banks
            card = node.attachNewNode(_flame_card())
            card.setH(heading)
        node.setScale(scale[0], scale[0], scale[1])
        node.setColor(*color)
    flame.setTexture(_flame_texture())
    flame.setLightOff()
    flame.setShaderOff()
    flame.setTwoSided(True)
    flame.setDepthWrite(False)
    flame.setBin("fixed", 15)  # after the ships, before the bullets
    flame.setAttrib(
        ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
    )
    return flame


def _flame_card() -> PandaNode:
    card = CardMaker("flame_card")
    card.setFrame(-0.5, 0.5, -1.0, 0.0)  # from the nozzle (Z 0) down to the tip (Z -1)
    return card.generate()


_FLAME_TEXTURES: list[Texture] = []


def _flame_texture() -> Texture:
    """Make the flame's texture: white, with the flame's shape in its alpha.

    Widest and brightest at the nozzle (the top row), narrowing and fading out towards the tip, soft at the edges. Built
    once.
    """
    if _FLAME_TEXTURES:
        return _FLAME_TEXTURES[0]
    width, height = FLAME_TEXTURE_SIZE
    image = PNMImage(width, height, 4)
    for row in range(height):
        along = row / (height - 1)  # 0 at the nozzle, 1 at the tip
        half_width = max((1 - along) ** 0.3, 1e-6)
        for column in range(width):
            across = abs((column + 0.5) / width * 2 - 1)
            edge = max(0.0, 1 - (across / half_width) ** 2)
            image.setXelA(column, row, 1, 1, 1, edge * (1 - along) ** 0.9)
    texture = Texture("flame")
    texture.load(image)
    texture.setWrapU(Texture.WM_clamp)
    texture.setWrapV(Texture.WM_clamp)
    _FLAME_TEXTURES.append(texture)
    return texture
