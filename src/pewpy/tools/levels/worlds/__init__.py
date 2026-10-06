"""The worlds' plans, one module per world, in playing order."""

from pewpy.tools.levels.worlds.bright_ridges import BRIGHT_RIDGES
from pewpy.tools.levels.worlds.heartland import HEARTLAND
from pewpy.tools.levels.worlds.highlands import HIGHLANDS
from pewpy.tools.levels.worlds.ironworks import IRONWORKS
from pewpy.tools.levels.worlds.lush_veld import LUSH_VELD
from pewpy.tools.levels.worlds.metropolis import METROPOLIS
from pewpy.tools.levels.worlds.rust_pan import RUST_PAN
from pewpy.tools.levels.worlds.wildwood import WILDWOOD

__all__ = ["WORLDS"]

WORLDS = (HIGHLANDS, WILDWOOD, LUSH_VELD, HEARTLAND, RUST_PAN, BRIGHT_RIDGES, IRONWORKS, METROPOLIS)
