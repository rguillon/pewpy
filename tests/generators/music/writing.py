"""A song being written, to write parts into."""

import random
from dataclasses import replace

from pewpy.generators.music.harmony import NOTES
from pewpy.generators.music.plans import PLANS
from pewpy.generators.music.writer import Writer


def writer(**plan: object) -> Writer:
    """Start writing the first song (its plan changed as told), from its own seed."""
    made = replace(PLANS[0], **plan)
    return Writer(made, random.Random(made.seed), NOTES[made.key])
