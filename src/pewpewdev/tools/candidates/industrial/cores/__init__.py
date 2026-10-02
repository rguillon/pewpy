"""The industrial ships' core hulls, each in its own module."""

from pewpewdev.tools.candidates.industrial.cores.arrow import core_arrow
from pewpewdev.tools.candidates.industrial.cores.block import core_block
from pewpewdev.tools.candidates.industrial.cores.crescent import core_crescent
from pewpewdev.tools.candidates.industrial.cores.cross import core_cross
from pewpewdev.tools.candidates.industrial.cores.diamond import core_diamond
from pewpewdev.tools.candidates.industrial.cores.egg import core_egg
from pewpewdev.tools.candidates.industrial.cores.frame import core_frame
from pewpewdev.tools.candidates.industrial.cores.segmented import core_segmented
from pewpewdev.tools.candidates.industrial.cores.spindle import core_spindle
from pewpewdev.tools.candidates.industrial.cores.wedge import core_wedge

CORES = [core_spindle, core_block, core_wedge, core_egg, core_segmented, core_cross, core_crescent, core_frame,
         core_diamond, core_arrow]  # fmt: skip
