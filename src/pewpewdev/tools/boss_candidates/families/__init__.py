"""The cores' families, each in its own module: a family draws a core's outline on the canvas, around `mx`, from
`top` to `bottom`, `half` wide on each side.
"""

from collections.abc import Callable

from pewpewdev.tools.boss_candidates.families.barge import barge
from pewpewdev.tools.boss_candidates.families.blade import blade
from pewpewdev.tools.boss_candidates.families.carrier import carrier
from pewpewdev.tools.boss_candidates.families.chain import chain
from pewpewdev.tools.boss_candidates.families.citadel import citadel
from pewpewdev.tools.boss_candidates.families.crescent import crescent
from pewpewdev.tools.boss_candidates.families.dreadnought import dreadnought
from pewpewdev.tools.boss_candidates.families.flying_wing import flying_wing
from pewpewdev.tools.boss_candidates.families.fortress import fortress
from pewpewdev.tools.boss_candidates.families.gunline import gunline
from pewpewdev.tools.boss_candidates.families.hammerhead import hammerhead
from pewpewdev.tools.boss_candidates.families.modular import modular
from pewpewdev.tools.boss_candidates.families.mothership import mothership
from pewpewdev.tools.boss_candidates.families.ring_cluster import ring_cluster
from pewpewdev.tools.boss_candidates.families.spider import spider
from pewpewdev.tools.boss_candidates.families.station import station
from pewpewdev.tools.boss_candidates.families.trident import trident
from pewpewdev.tools.boss_candidates.families.twin_hull import twin_hull
from pewpewdev.tools.candidates.canvas import Canvas, Rng

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
