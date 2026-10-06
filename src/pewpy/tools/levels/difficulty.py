"""How hard each level is, and what that sets: the scroll speed, the threat, the groups."""

# Difficulty: 1 (the first level) to 20 (the last one).
MAX_DIFFICULTY = 20
SCROLL_SPEED = (0.2, 0.31)  # at the easiest and the hardest level
THREAT = (8600, 22500)  # a half level's enemies, in points, at the easiest and the hardest level...
THREAT_CURVE = 0.6  # ...rising fast at first, then slower
GROWTH = 1.073  # groups are this much bigger for each step of difficulty


def difficulty(world: int, level: int) -> int:
    """Level `level` of world `world` (both from 1)."""
    return 2 * (world - 1) + level


def between(low_high: tuple[float, float], d: int) -> float:
    """Return the value for difficulty `d`, from `low` at 1 to `high` at MAX_DIFFICULTY."""
    low, high = low_high
    return low + (high - low) * (d - 1) / (MAX_DIFFICULTY - 1)


def budget(d: int) -> float:
    """Return a half level's threat at difficulty `d` (beyond MAX_DIFFICULTY it keeps growing)."""
    return THREAT[0] + (THREAT[1] - THREAT[0]) * ((d - 1) / (MAX_DIFFICULTY - 1)) ** THREAT_CURVE
