"""The cores' families, each in its own module.

A family draws a core's outline on the canvas, around `mx`, from `top` to `bottom`, `half` wide on each side.
"""

from collections.abc import Callable

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.bosses.families.barge import barge
from pewpy.generators.models.bosses.families.blade import blade
from pewpy.generators.models.bosses.families.carrier import carrier
from pewpy.generators.models.bosses.families.chain import chain
from pewpy.generators.models.bosses.families.citadel import citadel
from pewpy.generators.models.bosses.families.crescent import crescent
from pewpy.generators.models.bosses.families.dreadnought import dreadnought
from pewpy.generators.models.bosses.families.flying_wing import flying_wing
from pewpy.generators.models.bosses.families.fortress import fortress
from pewpy.generators.models.bosses.families.gunline import gunline
from pewpy.generators.models.bosses.families.hammerhead import hammerhead
from pewpy.generators.models.bosses.families.modular import modular
from pewpy.generators.models.bosses.families.mothership import mothership
from pewpy.generators.models.bosses.families.ring_cluster import ring_cluster
from pewpy.generators.models.bosses.families.spider import spider
from pewpy.generators.models.bosses.families.station import station
from pewpy.generators.models.bosses.families.trident import trident
from pewpy.generators.models.bosses.families.twin_hull import twin_hull
from pewpy.generators.models.common.geometry import Rng

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
