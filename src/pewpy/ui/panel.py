"""Cockpit instrument panels for the 2D overlay: metal plates with bevelled edges and screws, recessed displays.

Everything is flat cards, drawn in the order they're made (later on top), in aspect2d units.
"""

from typing import Literal

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, NodePath, TextNode, TransparencyAttrib

Color = tuple[float, float, float, float]
TextAlign = Literal[0, 1, 2, 3, 4, 5]  # TextNode.ALeft, ARight, ACenter...

RIM: Color = (0.03, 0.035, 0.04, 1)  # the dark edge around a plate
HIGHLIGHT: Color = (0.36, 0.39, 0.42, 1)  # a plate's top-left bevel, catching the light
SHADOW: Color = (0.08, 0.09, 0.1, 1)  # its bottom-right bevel
FACE: Color = (0.17, 0.19, 0.21, 1)  # gunmetal
SCREW: Color = (0.42, 0.44, 0.46, 1)
SCREW_SLOT: Color = (0.1, 0.11, 0.12, 1)
DISPLAY: Color = (0.02, 0.035, 0.03, 1)  # a display's glass, unlit
LABEL: Color = (0.68, 0.71, 0.74, 1)  # the stencilled words on a plate
BEVEL = 0.006  # width of a plate's bevel and rim
SCREW_SIZE = 0.014
LABEL_SCALE = 0.026


def card(parent: NodePath, left: float, right: float, bottom: float, top: float, color: Color) -> NodePath:
    """Return a flat rectangle of `color` under `parent`."""
    maker = CardMaker("panel_card")
    maker.setFrame(left, right, bottom, top)
    node = parent.attachNewNode(maker.generate())
    node.setColor(color)
    if color[3] < 1:
        node.setTransparency(TransparencyAttrib.MAlpha)
    return node


def plate(parent: NodePath, left: float, right: float, bottom: float, top: float) -> NodePath:
    """Return a metal plate: a dark rim, a bevel lit from the top left, a screw in each corner."""
    root = parent.attachNewNode("plate")
    e = BEVEL
    card(root, left, right, bottom, top, RIM)
    card(root, left + e, right - 2 * e, bottom + 2 * e, top - e, HIGHLIGHT)
    card(root, left + 2 * e, right - e, bottom + e, top - 2 * e, SHADOW)
    card(root, left + 2 * e, right - 2 * e, bottom + 2 * e, top - 2 * e, FACE)
    inset = 2 * e + SCREW_SIZE
    for x in (left + inset, right - inset):
        for z in (bottom + inset, top - inset):
            screw(root, x, z)
    return root


def screw(parent: NodePath, x: float, z: float) -> None:
    """Draw a flat-head screw at (x, z): a small lit disc (a turned square) and its slot."""
    half = SCREW_SIZE / 2
    head = card(parent, -half, half, -half, half, SCREW)
    head.setPos(x, 0, z)
    head.setR(45)
    slot = card(parent, -half, half, -half / 4, half / 4, SCREW_SLOT)
    slot.setPos(x, 0, z)
    slot.setR(-30 if (x + z) % 0.1 < 0.05 else 25)  # not all turned the same way


def display(parent: NodePath, left: float, right: float, bottom: float, top: float) -> NodePath:
    """Return a recessed display: shadowed at the top left, lit at the bottom right, a faint glint on its glass."""
    root = parent.attachNewNode("display")
    e = BEVEL / 2
    card(root, left - e, right + e, bottom - e, top + e, HIGHLIGHT)
    card(root, left - e, right, bottom, top + e, RIM)
    card(root, left, right, bottom, top, DISPLAY)
    card(root, left, right, top - (top - bottom) * 0.3, top, (1, 1, 1, 0.035))
    return root


def text(
    parent: NodePath,
    x: float,
    z: float,
    scale: float,
    color: Color,
    align: TextAlign = TextNode.ALeft,
    content: str = "",
) -> OnscreenText:
    """Return a text whose baseline is at (x, z), which can change."""
    return OnscreenText(text=content, pos=(x, z), align=align, scale=scale, fg=color, mayChange=True, parent=parent)


def label(parent: NodePath, x: float, z: float, content: str, align: TextAlign = TextNode.ALeft) -> OnscreenText:
    """Return a small stencilled word on a plate."""
    return text(parent, x, z, LABEL_SCALE, LABEL, align, content)
