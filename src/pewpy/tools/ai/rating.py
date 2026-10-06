"""Rating every level for every ship: how often the trained brain flying that ship clears it.

By the game's rules (all its lives, the weapons at level 1), over RUNS runs that differ by their randomness. The
rating is that clear rate: the lower, the harder the level.
"""

from collections.abc import Callable, Iterable
from concurrent.futures import Executor, ProcessPoolExecutor
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

from pewpy import config
from pewpy.game.level import Level, load_worlds
from pewpy.tools.ai import files
from pewpy.tools.ai.brain import Brain
from pewpy.tools.ai.episode import Outcome, play
from pewpy.tools.ai.learning import default_workers

RUNS = 10


@cache
def places() -> tuple[tuple[str, Level], ...]:
    """Every level with its place, like ("2-5", level), in playing order."""
    return tuple(
        (f"{w}-{n}", level)
        for w, world in enumerate(load_worlds(), start=1)
        for n, level in enumerate(world.levels, start=1)
    )


@dataclass(frozen=True)
class Rating:
    """How a level went for a ship over its runs."""

    place: str
    name: str
    clear_rate: float  # from 0 to 100: the share of runs that cleared the level, in %
    progress: float  # how far the runs got on average (see episode.Outcome.progress: 2 is cleared)
    lives_lost: float  # per run, on average


def rate_run(task: tuple[np.ndarray, tuple[int, ...], str, int, int]) -> Outcome:
    """One run of a level by the game's rules (in a worker process)."""
    weights, hidden, ship, index, seed = task
    return play(places()[index][1], Brain(weights, hidden), ship, seed, lives=config.PLAYER_LIVES)


def summarize(place: str, level: Level, outcomes: list[Outcome]) -> Rating:
    """Sum up a level's runs as its rating."""
    return Rating(
        place=place,
        name=level.name,
        clear_rate=round(100.0 * sum(outcome.cleared for outcome in outcomes) / len(outcomes), 1),
        progress=round(float(np.mean([outcome.progress for outcome in outcomes])), 3),
        lives_lost=round(float(np.mean([outcome.lives_lost for outcome in outcomes])), 2),
    )


def rate(
    ships: Iterable[str],
    folder: Path,
    runs: int = RUNS,
    workers: int | None = None,
    report: Callable[[str, Rating], None] = lambda _ship, _rating: None,
    stop: Callable[[], bool] = lambda: False,
    executor: Executor | None = None,
) -> dict[str, Any]:
    """Rate every level for each ship with the brain, if there is one; saved to ratings.json and returned."""
    ratings: dict[str, Any] = {"date": datetime.now(UTC).isoformat(timespec="seconds"), "runs": runs}
    training = files.load_training(folder)
    if training is None:
        return ratings | {"ships": {}}
    brain = training.brain
    ratings |= {"generation": training.generation, "ships": {}}
    with executor or ProcessPoolExecutor(max_workers=workers or default_workers()) as pool:
        for ship in ships:
            ship_ratings: dict[str, Any] = {"levels": []}
            ratings["ships"][ship] = ship_ratings
            for index, (place, level) in enumerate(places()):
                if stop():
                    return ratings
                tasks = [(brain.weights, brain.hidden, ship, index, seed) for seed in range(runs)]
                rating = summarize(place, level, list(pool.map(rate_run, tasks)))
                ship_ratings["levels"].append(asdict(rating))
                report(ship, rating)
    files.save_ratings(folder, ratings)
    return ratings
