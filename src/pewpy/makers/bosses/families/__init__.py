"""The cores' families, each in its own module.

A family draws a core's outline on the canvas, around `mx`, from `top` to `bottom`, `half` wide on each side.
"""

from collections.abc import Callable

from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.bosses.families.barge import barge
from pewpy.makers.bosses.families.blade import blade
from pewpy.makers.bosses.families.carrier import carrier
from pewpy.makers.bosses.families.chain import chain
from pewpy.makers.bosses.families.citadel import citadel
from pewpy.makers.bosses.families.crescent import crescent
from pewpy.makers.bosses.families.dreadnought import dreadnought
from pewpy.makers.bosses.families.flying_wing import flying_wing
from pewpy.makers.bosses.families.fortress import fortress
from pewpy.makers.bosses.families.gunline import gunline
from pewpy.makers.bosses.families.hammerhead import hammerhead
from pewpy.makers.bosses.families.modular import modular
from pewpy.makers.bosses.families.mothership import mothership
from pewpy.makers.bosses.families.ring_cluster import ring_cluster
from pewpy.makers.bosses.families.spider import spider
from pewpy.makers.bosses.families.station import station
from pewpy.makers.bosses.families.trident import trident
from pewpy.makers.bosses.families.twin_hull import twin_hull
from pewpy.makers.common.geometry import Rng

Family = Callable[[Rng, Canvas, float, float, float, float], None]
FAMILIES: dict[str, Family] = {
    "carrier": carrier,
    "dreadnought": dreadnought,
    "station": station,
    "hammerhead": hammerhead,
    "twin_hull": twin_hull,
    "flying_wing": flying_wing,
    "crescent": crescent,
    "modular": modular,
    "citadel": citadel,
    "spider": spider,
    "trident": trident,
    "barge": barge,
    "mothership": mothership,
    "chain": chain,
    "fortress": fortress,
    "blade": blade,
    "gunline": gunline,
    "ring_cluster": ring_cluster,
}
