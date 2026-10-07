"""What a core can carry on its sides, each in its own module."""

from pewpy.generators.models.bosses.appendages.arms import arms
from pewpy.generators.models.bosses.appendages.big_wings import big_wings
from pewpy.generators.models.bosses.appendages.halo import halo
from pewpy.generators.models.bosses.appendages.masts import masts
from pewpy.generators.models.bosses.appendages.nacelles import nacelles
from pewpy.generators.models.bosses.appendages.radiators import radiators
from pewpy.generators.models.bosses.appendages.spikes import spikes

APPENDAGES = [big_wings, arms, spikes, halo, nacelles, radiators, masts]
