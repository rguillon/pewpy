"""Making ships from the kit's parts (the enemies', or the player's)."""

from collections.abc import Callable

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.common.palette import GREYS, palette, pick_colors, pick_player_colors
from pewpy.generators.models.ships.kit import ARCHETYPES, PLAYER_ARCHETYPES, Ship
from pewpy.generators.models.ships.kit.archetypes import PLAYER_FIT

# How often each kind of ship is made.
SHARES = {"fighter": 0.24, "interceptor": 0.14, "bomber": 0.14, "drone": 0.16, "gunship": 0.16, "heavy": 0.16}
PLAYER_SHARES = {"vanguard": 0.34, "juggernaut": 0.33, "phantom": 0.33}
FLAMES = (4, 8)  # an enemy's flames' length, in cubes (at a fit of 1)
PLAYER_FLAMES = (16, 22)  # a player's ship's, in its recipe's cubes (made at PLAYER_FIT: 8 to 11 cubes)


def usual_fit(*, player: bool = False) -> float:
    """Return the fit ships are made at to be their recipes' usual size (see kit.Ship)."""
    return PLAYER_FIT if player else 1.0


def build(rng: Rng, kind: str, *, player: bool = False, fit: float | None = None) -> Ship:
    """Build a ship of a kind (see kit.ARCHETYPES, or kit.PLAYER_ARCHETYPES for a player's ship), at a fit."""
    archetype = (PLAYER_ARCHETYPES if player else ARCHETYPES)[kind]
    return archetype(rng, fit=usual_fit(player=player) if fit is None else fit)


def finish(rng: Rng, made: Ship, *, player: bool = False) -> Callable[[], dict]:
    """Pick a ship's colors and flames: return what makes its drawing."""
    colors = palette(GREYS, pick_player_colors(rng) if player else pick_colors(rng))
    flame = made.fitted(rng.randint(*(PLAYER_FLAMES if player else FLAMES)))

    def make() -> dict:
        return made.drawing(colors, flame, player=player)

    return make
