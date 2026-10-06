"""The cores' families, each in its own module.

A family draws a core's outline on the canvas, around `mx`, from `top` to `bottom`, `half` wide on each side.
"""

from collections.abc import Callable

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.boss_candidates.families.barge import barge
from pewpy.tools.boss_candidates.families.blade import blade
from pewpy.tools.boss_candidates.families.carrier import carrier
from pewpy.tools.boss_candidates.families.chain import chain
from pewpy.tools.boss_candidates.families.citadel import citadel
from pewpy.tools.boss_candidates.families.crescent import crescent
from pewpy.tools.boss_candidates.families.dreadnought import dreadnought
from pewpy.tools.boss_candidates.families.flying_wing import flying_wing
from pewpy.tools.boss_candidates.families.fortress import fortress
from pewpy.tools.boss_candidates.families.gunline import gunline
from pewpy.tools.boss_candidates.families.hammerhead import hammerhead
from pewpy.tools.boss_candidates.families.modular import modular
from pewpy.tools.boss_candidates.families.mothership import mothership
from pewpy.tools.boss_candidates.families.ring_cluster import ring_cluster
from pewpy.tools.boss_candidates.families.spider import spider
from pewpy.tools.boss_candidates.families.station import station
from pewpy.tools.boss_candidates.families.trident import trident
from pewpy.tools.boss_candidates.families.twin_hull import twin_hull
from pewpy.tools.common.geometry import Rng

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
