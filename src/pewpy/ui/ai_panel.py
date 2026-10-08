"""The AI playing screen's text, over the game (07-ai.md).

The text is made by a plain function (`playing_text`); AIPanel only draws it.
"""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode

TEXT_COLOR = (0.85, 0.88, 0.95, 1)
SCALE = 0.042
POSITION = (-1.2, 0.9)  # its top-left corner


def playing_text(generation: int | None, watching: str, start: str, games: int, cleared: int, best: int) -> str:
    """Write the AI playing screen's text: the brain, what it plays, how its games from the level picked went."""
    brain = "no brain yet: a new one plays" if generation is None else f"the brain at generation {generation}"
    lines = [f"AI PLAYING  {brain}, by the game's rules  (Esc: pick another level)", "", f"On screen: {watching}"]
    done = games - 1  # the one being played isn't over
    if done:
        lines.append(f"Games from {start}: {done}, {start} cleared in {cleared} ({100 * cleared / done:.0f}%)")
        lines.append(f"Best game: {best} level{'s' if best != 1 else ''} cleared")
    return "\n".join(lines)


class AIPanel:
    """The AI playing screen's text, drawn over the game."""

    def __init__(self, parent: NodePath) -> None:
        """Make the text over the game, hidden until `show`."""
        self.text = OnscreenText(
            text="", pos=POSITION, align=TextNode.ALeft, scale=SCALE, fg=TEXT_COLOR, mayChange=True, parent=parent
        )
        self.text.hide()

    def show(self, text: str) -> None:
        """Show the text (Panda3D remakes a text's geometry each time it is set: only when it changed)."""
        if self.text.getText() != text:
            self.text.setText(text)
        self.text.show()

    def hide(self) -> None:
        """Hide the text."""
        self.text.hide()
