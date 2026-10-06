"""What a core can carry on its sides, each in its own module."""

from pewpy.tools.boss_candidates.appendages.arms import arms
from pewpy.tools.boss_candidates.appendages.big_wings import big_wings
from pewpy.tools.boss_candidates.appendages.halo import halo
from pewpy.tools.boss_candidates.appendages.masts import masts
from pewpy.tools.boss_candidates.appendages.nacelles import nacelles
from pewpy.tools.boss_candidates.appendages.radiators import radiators
from pewpy.tools.boss_candidates.appendages.spikes import spikes

APPENDAGES = [big_wings, arms, spikes, halo, nacelles, radiators, masts]
