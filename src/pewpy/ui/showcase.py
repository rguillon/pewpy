"""The Models screen: every model in a slowly turning circle, each spinning, its name underneath.

For working on the models (pewpy.graphics.models): the screen can reload them without restarting the game.
"""

import math

from panda3d.core import NodePath, TextNode

DISTANCE = 3.3  # from the camera: about as far as the play area
RADIUS = 0.76  # world units: as wide as fits on the screen (about 0.9 each side at that distance)
MODEL_SIZE = 0.17
LABEL_SCALE = 0.032
LABEL_BELOW = 0.55  # names hang this much of the model's size under its middle, plus LABEL_GAP
LABEL_GAP = 0.07
SPIN_SPEED = 60.0  # degrees per second, each model around its own up axis (up the screen)
TURN_SPEED = 6.0  # degrees per second, the whole circle


class ModelShowcase:
    """Models on show in a turning circle, each with its name."""

    def __init__(
        self,
        entries: list[tuple[str, NodePath]],
        camera: NodePath,
        size: float = MODEL_SIZE,
        radius: float = RADIUS,
        stretch: float = 1.0,
    ) -> None:
        """Place the models around the circle.

        `entries`: (name, model) pairs; the models are copied, so they can be shared with the game. `size`: how big a 1
        x 1 x 1 model is drawn; `radius`: the circle's, up and down; `stretch`: how much wider it is across (on a wide
        screen, an ellipse uses the room on the sides).

        The circle hangs in front of the camera, facing it, so it's round and centered on the screen (the game's camera
        is tilted: on the play plane it would look squashed). The models go round it slowly, staying upright.
        """
        self.root = camera.attachNewNode("showcase")
        self.root.setY(DISTANCE)
        self.circle = self.root.attachNewNode("circle")
        self.radius, self.stretch = radius, stretch
        self.angles: list[float] = []
        self.slots: list[NodePath] = []
        self.spinners: list[NodePath] = []
        self.time = 0.0
        for index, (name, model) in enumerate(entries):
            self.angles.append(2 * math.pi * index / len(entries) + math.pi / 2)  # the first one at the top
            slot = self.circle.attachNewNode(name)
            spinner = slot.attachNewNode("spinner")
            model.copyTo(spinner)
            spinner.setScale(size)
            label = slot.attachNewNode(self._label(name))
            # Under the model, readable: not lit, not shaded, always drawn on top.
            label.setScale(LABEL_SCALE)
            label.setPos(0, -size, -size * LABEL_BELOW - LABEL_GAP)
            label.setLightOff()
            label.setShaderOff()
            label.setBin("fixed", 10)
            label.setDepthTest(False)
            label.setDepthWrite(False)
            self.slots.append(slot)
            self.spinners.append(spinner)
        self.update(0.0)

    def update(self, dt: float) -> None:
        """Turn the circle and spin the models."""
        self.time += dt
        turn = -math.radians(self.time * TURN_SPEED)  # clockwise
        for angle, slot, spinner in zip(self.angles, self.slots, self.spinners, strict=True):
            across, up = math.cos(angle + turn), math.sin(angle + turn)
            slot.setPos(across * self.radius * self.stretch, 0, up * self.radius)
            spinner.setH(self.time * SPIN_SPEED)

    def destroy(self) -> None:
        """Remove the showcase's nodes."""
        self.root.removeNode()

    def _label(self, name: str) -> TextNode:
        text = TextNode(f"label_{name}")
        text.setText(name)
        text.setAlign(TextNode.ACenter)
        text.setTextColor(0.8, 0.82, 0.9, 1)
        return text
