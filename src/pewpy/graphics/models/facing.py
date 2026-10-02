"""Turning models the way they go."""

import math


def facing_roll(dx: float, dz: float) -> float:
    """Roll angle (degrees) that turns a model pointing down the screen (-Z) to point along (dx, dz)."""
    return math.degrees(math.atan2(-dx, -dz))
