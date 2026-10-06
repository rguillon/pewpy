"""The AI screens' text (07-ai.md).

The brain's learning progress with each ship over the AI playing, and the ratings table. The texts are made by plain
functions (`learning_text`, `rating_columns`); AIPanel only draws them.
"""

from typing import Literal

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode

from pewpy.game.player import SHIPS
from pewpy.tools.ai.learning import Check, Report
from pewpy.tools.ai.rating import Rating

Color = tuple[float, float, float, float]
TextAlign = Literal[0, 1, 2, 3, 4, 5]  # TextNode.ALeft, ARight...

TEXT_COLOR: Color = (0.85, 0.88, 0.95, 1)
TITLE_COLOR: Color = (1.0, 0.9, 0.3, 1)
SCALE = 0.042
TABLE_SCALE = 0.034
ROW = 1.25  # a line's height, in text scales
ROWS_PER_COLUMN = 24  # the ratings table in two halves, side by side (worlds 1 to 4, then 5 to 8)
VALUE_WIDTH = 0.17  # each ship's column of the table
NAME_WIDTH = 0.5


def learning_text(report: Report | None, checks: Check, watching: str, error: str | None) -> str:
    """Write the AI learning screen's text: the generation, then how far the brain gets with each ship."""
    lines = ["AI LEARNING  (Esc: stop, it goes on from here next time)", ""]
    if report is None:
        lines.append("One brain for every ship: starting")
    else:
        worlds = f"{report.worlds} world{'s' if report.worlds > 1 else ''}"
        lines.append(f"One brain for every ship: generation {report.generation}  best {report.best:.0f}  on {worlds}")
    for ship, spec in SHIPS.items():
        if ship in checks:
            cleared, progress = checks[ship]
            state = f"clears {100 * cleared:.0f}% of the levels, gets {100 * progress:.0f}% of the way"
        else:
            state = "not checked yet"
        lines.append(f"  {spec.name:<11} {state}")
    lines += ["", watching]
    if error:
        lines += ["", f"Stopped: {error}"]
    return "\n".join(lines)


def playing_text(generation: int | None, watching: str, reached: dict[str, int], levels: int) -> str:
    """Write the AI playing screen's text: the brain, what it plays, and how far each ship got in a game."""
    brain = "no brain yet: a new one plays" if generation is None else f"the brain at generation {generation}"
    lines = [f"AI PLAYING  {brain}, by the game's rules  (Esc: back)", "", f"On screen: {watching}", ""]
    for ship, spec in SHIPS.items():
        if ship in reached:
            lines.append(f"  {spec.name:<11} best game: {reached[ship]}/{levels} levels cleared")
    return "\n".join(lines)


def rating_title(ships: list[str], runs: int, rating: str, saved_to: str, error: str | None) -> str:
    """Write the AI rating screen's title and status."""
    if not ships:
        return "AI RATING\n\nNo ship has learned yet: start AI learning first.  (Esc: back)"
    head = f"AI RATING  clear rate in % over {runs} runs, the lower the harder  (Esc: stop)"
    status = f"Saved to {saved_to}" if saved_to else rating
    return f"{head}\n{f'Stopped: {error}' if error else status}"


def rating_columns(places: list[tuple[str, str]], ships: list[str], table: dict[str, list[Rating]]) -> list[list[str]]:
    """Return the table as columns of lines: for each half, the levels' places and names, then each ship's rates."""
    columns = []
    for start in range(0, len(places), ROWS_PER_COLUMN):
        half = places[start : start + ROWS_PER_COLUMN]
        columns.append(["LEVEL", *(f"{place}  {name}" for place, name in half)])
        for ship in ships:
            rates = table.get(ship, [])
            cells = [
                f"{rates[index].clear_rate:.0f}" if index < len(rates) else ""
                for index in range(start, start + len(half))
            ]
            columns.append([SHIPS[ship].name[:5], *cells])
    return columns


class AIPanel:
    """The AI screens' text, drawn over the game."""

    def __init__(self, parent: NodePath) -> None:
        self.root = parent.attachNewNode("ai_panel")
        self.texts: list[OnscreenText] = []
        self.shown: list[str] = []

    def clear(self) -> None:
        """Remove the texts."""
        for text in self.texts:
            text.destroy()
        self.texts, self.shown = [], []

    def show_learning(self, text: str) -> None:
        """Show the AI learning screen's text."""
        self._show([(text, -1.2, 0.9, TextNode.ALeft, SCALE, TEXT_COLOR)])

    def show_rating(self, title: str, columns: list[list[str]], ships: int) -> None:
        """Show the AI rating screen's title and table."""
        texts: list[tuple[str, float, float, TextAlign, float, Color]] = [
            (title, -1.2, 0.9, TextNode.ALeft, SCALE, TITLE_COLOR)
        ]
        x = -1.2
        for index, column in enumerate(columns):
            first_of_half = index % (ships + 1) == 0
            if first_of_half and index:
                x += 0.08
            align: TextAlign = TextNode.ALeft if first_of_half else TextNode.ARight
            width = NAME_WIDTH if first_of_half else VALUE_WIDTH
            anchor = x if first_of_half else x + width
            texts.append(("\n".join(column), anchor, 0.75, align, TABLE_SCALE, TEXT_COLOR))
            x += width
        self._show(texts)

    def _show(self, texts: list[tuple[str, float, float, TextAlign, float, Color]]) -> None:
        """Rebuild the texts only when they changed (Panda3D remakes a text's geometry each time it is set)."""
        wanted = [text for text, *_ in texts]
        if wanted == self.shown:
            return
        if len(texts) != len(self.texts):
            self.clear()
            for text, x, z, align, scale, color in texts:
                self.texts.append(
                    OnscreenText(
                        text=text, pos=(x, z), align=align, scale=scale, fg=color, mayChange=True, parent=self.root
                    )
                )
        else:
            for node, (text, *_rest) in zip(self.texts, texts, strict=True):
                node.setText(text)
        self.shown = wanted
