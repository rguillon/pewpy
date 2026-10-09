"""Making ships from the catalog's parts (the enemies', or the player's), and finishing them: colors and flames."""

from collections.abc import Callable

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.common.palette import GREYS, palette, pick_colors, pick_player_colors
from pewpy.generators.models.ships.placing import make_ship
from pewpy.generators.models.ships.ship import Ship

FLAMES = (4, 8)  # an enemy's flames' length, in cubes
PLAYER_FLAMES = (8, 11)  # a player's ship's


def build(rng: Rng, wanted: tuple[float, float], *, player: bool = False) -> Ship:
    """Build a ship of about `wanted` cubes, across and along (see placing.make_ship)."""
    return make_ship(rng, wanted, player=player)


def finish(rng: Rng, made: Ship, *, player: bool = False) -> Callable[[], dict]:
    """Pick a ship's colors and flames: return what makes its drawing."""
    colors = palette(GREYS, pick_player_colors(rng) if player else pick_colors(rng))
    flame = rng.randint(*(PLAYER_FLAMES if player else FLAMES))

    def make() -> dict:
        return made.drawing(colors, flame, player=player)

    return make
