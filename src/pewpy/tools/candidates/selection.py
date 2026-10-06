"""Making ships from the kit's parts (the enemies', or the player's), and keeping the most different ones."""

import random
from collections.abc import Callable

from pewpy.tools.candidates.kit import ARCHETYPES, PLAYER_ARCHETYPES
from pewpy.tools.common.geometry import Rng
from pewpy.tools.common.palette import GREYS, palette, pick_colors, pick_player_colors
from pewpy.tools.common.variety import features, most_different

# Shares of each kind of ship, by --kind: all of them, or one.
MIXES: dict[str, dict[str, float]] = {
    "all": {"fighter": 0.24, "interceptor": 0.14, "bomber": 0.14, "drone": 0.16, "gunship": 0.16, "heavy": 0.16},
    **{name: {name: 1.0} for name in ARCHETYPES},
}
PLAYER_MIXES: dict[str, dict[str, float]] = {
    "all": {"vanguard": 0.34, "juggernaut": 0.33, "phantom": 0.33},
    **{name: {name: 1.0} for name in PLAYER_ARCHETYPES},
}
LARGEST = (35, 34)  # an enemy's columns and rows, at most
PLAYER_LARGEST = (43, 44)  # a player's ship's, in its finer cubes
FLAMES = (4, 8)  # an enemy's flames' length, in cubes
PLAYER_FLAMES = (16, 22)  # a player's ship's, in its finer cubes (like the game's ships)


def ship(rng: Rng, kind: str, *, player: bool = False) -> tuple[list[float], Callable[[], dict]] | None:
    """Make one ship of a kind (see kit.ARCHETYPES, or kit.PLAYER_ARCHETYPES for a player's ship).

    Return its features, and what makes its drawing.
    """
    made = (PLAYER_ARCHETYPES if player else ARCHETYPES)[kind](rng)
    width, length = made.size()
    largest_width, largest_length = PLAYER_LARGEST if player else LARGEST
    if width > largest_width or length > largest_length:
        return None
    rows = made.plan()
    colors = palette(GREYS, pick_player_colors(rng) if player else pick_colors(rng))
    flame = rng.randint(*(PLAYER_FLAMES if player else FLAMES))

    def make() -> dict:
        return made.drawing(colors, flame, player=player)

    return features(rows, made.symmetric), make


def generate(count: int, kind: str, seed: int, pool_factor: int, *, player: bool = False) -> list[dict]:
    """Generate `count` drawings of `kind`, keeping the most different of `pool_factor` times as many."""
    rng = random.Random(seed)
    drawings = []
    shares = (PLAYER_MIXES if player else MIXES)[kind]
    for index, (group, share) in enumerate(shares.items()):
        wanted = count - len(drawings) if index == len(shares) - 1 else round(count * share)
        pool = [made for _ in range(wanted * pool_factor) if (made := ship(rng, group, player=player)) is not None]
        if pool:
            drawings += [make() for make in most_different(pool, wanted)]
    rng.shuffle(drawings)
    return drawings
