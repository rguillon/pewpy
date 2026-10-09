"""Making ships from the catalog's parts (the player's, the enemies', the bosses'); finishing them: colors, flames."""

from collections.abc import Callable
from dataclasses import dataclass

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.common.palette import GREYS, palette, pick_colors, pick_player_colors
from pewpy.generators.models.ships.placing import Maker
from pewpy.generators.models.ships.ship import Ship


@dataclass(frozen=True)
class Asked:
    """What's asked of a ship besides its size: its destroyable parts, symmetric or lopsided (or either, None), its
    weapons at least.
    """  # noqa: D205 - the summary needs two lines

    parts: int = 0
    symmetric: bool | None = None
    least_armed: int = 1


FLAMES = (4, 8)  # an enemy's flames' length, in cubes...
PLAYER_FLAMES = (8, 11)  # ...a player's ship's...
FLAME_ROWS = 25  # ...on a ship up to this many rows long; longer as much as a longer one is *(placeholder)*


def build(rng: Rng, wanted: tuple[float, float], *, player: bool = False, asked: Asked | None = None) -> Ship:
    """Build a ship of about `wanted` cubes, across and along, with what's `asked` of it (see placing.Maker)."""
    return maker(rng, wanted, player=player, asked=asked).make()


def maker(rng: Rng, wanted: tuple[float, float], *, player: bool = False, asked: Asked | None = None) -> Maker:
    """Return what makes a ship of about `wanted` cubes, with what's `asked` of it: see placing.Maker."""
    asked = asked or Asked()
    return Maker(rng, wanted, player, asked.parts, asked.symmetric, asked.least_armed)


def finish(rng: Rng, made: Ship, *, player: bool = False) -> Callable[[], dict]:
    """Pick a ship's colors and flames (longer on a longer ship): return what makes its drawing."""
    colors = palette(GREYS, pick_player_colors(rng) if player else pick_colors(rng))
    flame = round(rng.randint(*(PLAYER_FLAMES if player else FLAMES)) * max(1.0, made.size()[1] / FLAME_ROWS))

    def make() -> dict:
        return made.drawing(colors, flame, player=player)

    return make
