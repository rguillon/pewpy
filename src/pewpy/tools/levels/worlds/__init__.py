"""The worlds' plans, one module per world, in playing order."""

from pewpy.tools.levels.worlds.archipelago import ARCHIPELAGO
from pewpy.tools.levels.worlds.fenlands import FENLANDS
from pewpy.tools.levels.worlds.heartland import HEARTLAND
from pewpy.tools.levels.worlds.highlands import HIGHLANDS
from pewpy.tools.levels.worlds.ironworks import IRONWORKS
from pewpy.tools.levels.worlds.metropolis import METROPOLIS
from pewpy.tools.levels.worlds.steamvale import STEAMVALE
from pewpy.tools.levels.worlds.wildwood import WILDWOOD

__all__ = ["WORLDS"]

WORLDS = (HIGHLANDS, WILDWOOD, FENLANDS, HEARTLAND, ARCHIPELAGO, STEAMVALE, IRONWORKS, METROPOLIS)
