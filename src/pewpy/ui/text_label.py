"""The texts over the ground, in a console: the browsers' and the screenshots'.

One factory for all of them, so a text over the ground looks the same wherever it is: centred, with a drop shadow so
it reads against whatever scrolls behind it. `TextsView` holds those texts and takes them away again; a view of its
own adds its own (see menu_view.py for the one under a plate, in world units).
"""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode

from pewpy.ui.menu_view import SHADOW_OFFSET, TEXT_SHADOW

Color = tuple[float, float, float, float]


def centered(parent: NodePath, z: float, scale: float, color: Color, wordwrap: float | None = None) -> OnscreenText:
    """Return a text centred on the screen, `z` up from its middle, empty until it's told what to say.

    It has a drop shadow, so it reads against whatever scrolls behind it.
    """
    return OnscreenText(
        text="",
        pos=(0, z),
        scale=scale,
        fg=color,
        shadow=TEXT_SHADOW,
        shadowOffset=SHADOW_OFFSET,
        align=TextNode.ACenter,
        wordwrap=wordwrap,
        mayChange=True,
        parent=parent,
    )


class TextsView:
    """A set of texts over the ground, under one node, each made empty and named by the view that owns it."""

    def __init__(self, parent: NodePath, name: str) -> None:
        """Make the view's nodes under `parent`: nothing written until the texts are told what to say."""
        self.root = parent.attachNewNode(name)
        self.texts: list[OnscreenText] = []

    def centered_text(self, z: float, scale: float, color: Color, wordwrap: float | None = None) -> OnscreenText:
        """Return a text of this view, centred, and keep it to take it away on `destroy`."""
        text = centered(self.root, z, scale, color, wordwrap=wordwrap)
        self.texts.append(text)
        return text

    def destroy(self) -> None:
        """Remove the view's nodes."""
        for text in self.texts:
            text.destroy()
        self.root.removeNode()
