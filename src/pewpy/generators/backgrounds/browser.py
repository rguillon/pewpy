"""The backgrounds browser of the Dev menu: background candidates, one theme at a time (see the package).

Left and Right go from one theme to the next, Space makes a new candidate of the theme (another seed). Nothing is
saved: a candidate is made again from its theme and seed. Independent from showing: the app shows `level`.
"""

import random
from dataclasses import dataclass, field
from typing import Any

from pewpy.game.level import Level
from pewpy.generators.backgrounds.candidate import candidate
from pewpy.generators.backgrounds.themes import THEMES

SCROLL_SPEED = 0.2  # a level's usual speed: the candidates scroll at it
SEEDS = 1_000_000  # a candidate's seed is below this
LEVEL_FIELDS = ("background", "scenery", "time_of_day", "clouds", "background_seed")  # what a candidate gives a level


@dataclass
class BackgroundBrowser:
    """The themes, the one on show, and its candidate (made from the theme and a seed)."""

    rng: random.Random = field(default_factory=random.Random)
    index: int = 0
    seed: int = 0
    made: dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        """Make a candidate of the first theme to show."""
        self.generate()

    @property
    def theme(self) -> str:
        """Return the theme on show."""
        return list(THEMES)[self.index]

    def move(self, step: int) -> None:
        """Show the next theme (step 1) or the previous one (-1), wrapping around, with a new candidate of it."""
        self.index = (self.index + step) % len(THEMES)
        self.generate()

    def generate(self) -> None:
        """Make a new candidate of the theme on show: another seed."""
        self.seed = self.rng.randrange(SEEDS)
        self.made = candidate(self.theme, self.seed)

    def level(self) -> Level:
        """Return the candidate as a level without waves, to show its background."""
        fields = {key: self.made[key] for key in LEVEL_FIELDS}
        return Level(name=self.made["name"], scroll_speed=SCROLL_SPEED, waves=(), **fields)

    def title(self) -> str:
        """Return the candidate's name, theme and number among the themes."""
        return f"{self.made['name']}: {self.theme}  ({self.index + 1}/{len(THEMES)})"

    def details(self) -> str:
        """Return what makes the candidate again (its theme and seed) and what a level says of it."""
        made = self.made
        return f"seed {self.seed}   preset {made['background']}   {made['time_of_day']}   clouds {made['clouds']}"
