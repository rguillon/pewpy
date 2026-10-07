"""What a core can carry on its sides, each in its own module."""

from pewpy.makers.bosses.appendages.arms import arms
from pewpy.makers.bosses.appendages.big_wings import big_wings
from pewpy.makers.bosses.appendages.halo import halo
from pewpy.makers.bosses.appendages.masts import masts
from pewpy.makers.bosses.appendages.nacelles import nacelles
from pewpy.makers.bosses.appendages.radiators import radiators
from pewpy.makers.bosses.appendages.spikes import spikes

APPENDAGES = [big_wings, arms, spikes, halo, nacelles, radiators, masts]
