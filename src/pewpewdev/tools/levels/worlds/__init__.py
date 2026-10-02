"""The worlds' plans, one module per world, in playing order."""

from pewpewdev.tools.levels.worlds.archipelago import ARCHIPELAGO
from pewpewdev.tools.levels.worlds.canyonlands import CANYONLANDS
from pewpewdev.tools.levels.worlds.fenlands import FENLANDS
from pewpewdev.tools.levels.worlds.heartland import HEARTLAND
from pewpewdev.tools.levels.worlds.highlands import HIGHLANDS
from pewpewdev.tools.levels.worlds.ironworks import IRONWORKS
from pewpewdev.tools.levels.worlds.metropolis import METROPOLIS
from pewpewdev.tools.levels.worlds.wildwood import WILDWOOD

__all__ = ["WORLDS"]

WORLDS = (HIGHLANDS, WILDWOOD, FENLANDS, HEARTLAND, ARCHIPELAGO, CANYONLANDS, IRONWORKS, METROPOLIS)
