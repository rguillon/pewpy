"""Win rates: how often the brain flying each ship clears every level (`make winrate`), saving nothing.

Over RUNS runs that differ by their randomness, with one life by default (as training does).
"""

from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor
from functools import cache

import numpy as np

from pewpy.ai.brain import Brain
from pewpy.ai.training.episode import play
from pewpy.ai.training.learning import default_workers
from pewpy.game.level import Level, load_worlds

RUNS = 10


@cache
def places() -> tuple[tuple[str, Level], ...]:
    """Every level with its place, like ("2-5", level), in playing order."""
    return tuple(
        (f"{w}-{n}", level)
        for w, world in enumerate(load_worlds(), start=1)
        for n, level in enumerate(world.levels, start=1)
    )


def win_run(task: tuple[np.ndarray, tuple[int, ...], str, int, int, int]) -> bool:
    """Whether a run of a level with `lives` clears it (in a worker process)."""
    weights, hidden, ship, index, seed, lives = task
    return play(places()[index][1], Brain(weights, hidden), ship, seed, lives=lives).cleared


def win_rates(
    brain: Brain,
    ships: Iterable[str],
    runs: int = RUNS,
    lives: int = 1,
    workers: int | None = None,
    report: Callable[[str, str, dict[str, float]], None] = lambda _place, _name, _rates: None,
) -> dict[str, dict[str, float]]:
    """Play every level `runs` times with each ship: for each level's place, each ship's share of runs cleared.

    `report` gets each level's place, name and rates as they come, in playing order.
    """
    ships = list(ships)
    plays = [(ship, seed) for ship in ships for seed in range(runs)]
    tasks = [
        (brain.weights, brain.hidden, ship, index, seed, lives)
        for index in range(len(places()))
        for ship, seed in plays
    ]
    rates: dict[str, dict[str, float]] = {}
    with ProcessPoolExecutor(max_workers=workers or default_workers()) as pool:
        results = pool.map(win_run, tasks)
        for place, level in places():
            cleared = [next(results) for _ in plays]
            rates[place] = {ship: float(np.mean(cleared[n * runs : (n + 1) * runs])) for n, ship in enumerate(ships)}
            report(place, level.name, rates[place])
    return rates
