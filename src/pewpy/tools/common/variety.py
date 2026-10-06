"""Keeping the most different of many candidates: by their features, each next one the farthest from those kept."""

import math


def features(rows: list[str], symmetric: bool) -> list[float]:
    """For telling ships apart: the outline shrunk to 8 x 8, the size, the proportions, symmetry, how full."""
    height, width = len(rows), len(rows[0])
    grid = []
    for gy in range(8):
        for gx in range(8):
            y0, x0 = gy * height // 8, gx * width // 8
            y1, x1 = max(y0 + 1, (gy + 1) * height // 8), max(x0 + 1, (gx + 1) * width // 8)
            cells = [rows[y][x] != "." for y in range(y0, y1) for x in range(x0, x1)]
            grid.append(sum(cells) / len(cells))
    filled = sum(char != "." for row in rows for char in row) / (width * height)
    return [*grid, 3 * width / 35, 3 * height / 35, 2 * math.log(width / height), 0.4 * (not symmetric), 2 * filled]


def most_different[T](pool: list[tuple[list[float], T]], count: int) -> list[T]:
    """`count` things of the pool, by their features: each next one is the farthest from all those already kept."""
    kept = [0]
    distance = [math.dist(f, pool[0][0]) for f, _ in pool]
    while len(kept) < min(count, len(pool)):
        index = max(range(len(pool)), key=distance.__getitem__)
        kept.append(index)
        distance = [min(d, math.dist(f, pool[index][0])) for d, (f, _) in zip(distance, pool, strict=True)]
    return [pool[index][1] for index in kept]
