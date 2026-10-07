"""The worlds' plans, one module per world, in playing order."""

from pewpy.generators.levels.worlds.bright_ridges import BRIGHT_RIDGES
from pewpy.generators.levels.worlds.heartland import HEARTLAND
from pewpy.generators.levels.worlds.highlands import HIGHLANDS
from pewpy.generators.levels.worlds.ironworks import IRONWORKS
from pewpy.generators.levels.worlds.lush_veld import LUSH_VELD
from pewpy.generators.levels.worlds.metropolis import METROPOLIS
from pewpy.generators.levels.worlds.rust_pan import RUST_PAN
from pewpy.generators.levels.worlds.wildwood import WILDWOOD

__all__ = ["WORLDS"]

WORLDS = (HIGHLANDS, WILDWOOD, LUSH_VELD, HEARTLAND, RUST_PAN, BRIGHT_RIDGES, IRONWORKS, METROPOLIS)
