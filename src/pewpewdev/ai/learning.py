"""Teaching the brain to play every level with every ship, by evolution strategies (evolution.py).

One brain flies all the ships, seeing which one it flies (sensors.py).

Each generation, every try of the population plays the same runs, one per ship, each on a level drawn among the
worlds open to it, with one life; its fitness is the mean of its runs' (episode.py). The tries play in worker
processes, in parallel. Every CHECK_EVERY generations the brain itself plays every level once with each ship: the
share it clears and how far it gets are its progress, and it is saved (files.py), so learning can stop at any time
and go on later.

A curriculum: a new brain trains on world 1 only; the next world opens once it gets OPEN_NEXT of the way into the
open worlds' levels on average (every ship's) at a check.
"""

import os
import random
from collections.abc import Callable, Iterable
from concurrent.futures import Executor, ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

from pewpewdev.ai import files
from pewpewdev.ai.brain import HIDDEN, Brain
from pewpewdev.ai.episode import play
from pewpewdev.ai.evolution import Evolution
from pewpy.game.level import Level, load_levels, load_worlds

CHECK_EVERY = 10  # generations
OPEN_NEXT = 0.5  # how far into the open worlds' levels (on average, 0.5: the final boss) for the next world to open


@cache
def _levels() -> tuple[Level, ...]:
    return tuple(load_levels())


@cache
def _world_sizes() -> tuple[int, ...]:
    """How many levels each world has, in order (_levels() has them one world after the other)."""
    return tuple(len(world.levels) for world in load_worlds())


def open_levels(worlds: int) -> int:
    """How many levels the first `worlds` worlds have (the levels training draws from)."""
    return min(sum(_world_sizes()[:worlds]), len(_levels())) or len(_levels())


Run = tuple[str, int, int]  # a ship, a level (its index) and the randomness's seed


def try_weights(task: tuple[np.ndarray, tuple[int, ...], tuple[Run, ...]]) -> float:
    """Play some runs with a brain's weights (in a worker process): its mean fitness."""
    weights, hidden, runs = task
    brain = Brain(weights, hidden)
    levels = _levels()
    return float(np.mean([play(levels[index], brain, ship, seed).fitness for ship, index, seed in runs]))


def check_level(task: tuple[np.ndarray, tuple[int, ...], str, int, int]) -> tuple[bool, float]:
    """Whether a brain clears a level with one life, and how far it gets (from 0 to 1: the boss destroyed)."""
    weights, hidden, ship, index, seed = task
    outcome = play(_levels()[index], Brain(weights, hidden), ship, seed)
    return outcome.cleared, outcome.progress / 2


def default_workers() -> int:
    """Return how many worker processes to use: the cores but one."""
    return max(1, (os.cpu_count() or 2) - 1)


Check = dict[str, tuple[float, float]]  # for each ship: the share of levels the brain clears, how far it gets (0 to 1)


@dataclass(frozen=True)
class Report:
    """How a generation went."""

    generation: int
    best: float  # the best try's fitness
    mean: float
    checks: Check | None = None  # when the brain was checked this generation
    worlds: int = 1  # the worlds it trains on


class Learner:
    """The brain's training, a generation at a time, with the `ships` given."""

    def __init__(self, ships: Iterable[str], folder: Path, executor: Executor, seed: int = 0) -> None:
        self.ships = list(ships)
        self.folder = folder
        self.executor = executor
        saved = files.load_training(folder)
        self.training = saved or files.Training(Brain.random(np.random.default_rng(seed), HIDDEN))
        # Levels to play, not cryptography; a resumed training draws new ones, not the start's again.
        self.rng = random.Random(seed * 1_000_003 + self.training.generation)
        self.evolution = Evolution(
            self.training.brain.weights.copy(), np.random.default_rng(seed + self.training.generation)
        )
        self.evolution.generation = self.training.generation

    @property
    def brain(self) -> Brain:
        """Return the brain being trained."""
        return self.training.brain

    def step(self) -> Report:
        """Play a generation: every try plays the runs, the evolution steps; check the brain every CHECK_EVERY."""
        levels = open_levels(self.training.worlds)
        runs = tuple((ship, self.rng.randrange(levels), self.rng.randrange(1_000_000)) for ship in self.ships)
        nudges, tries = self.evolution.ask()
        hidden = self.brain.hidden
        fitness = np.array(list(self.executor.map(try_weights, [(w, hidden, runs) for w in tries])))
        self.evolution.tell(nudges, fitness)
        self.training.brain = Brain(self.evolution.weights.copy(), hidden)
        self.training.generation = self.evolution.generation
        checks = None
        record: dict[str, Any] = {
            "generation": self.training.generation,
            "best": float(fitness.max()),
            "mean": float(fitness.mean()),
        }
        if self.training.generation % CHECK_EVERY == 0:
            checks = self.check()
            record |= {
                "cleared": float(np.mean([cleared for cleared, _ in checks.values()])),
                "progress": float(np.mean([gone for _, gone in checks.values()])),
                "worlds": self.training.worlds,
                "ships": {ship: {"cleared": cleared, "progress": gone} for ship, (cleared, gone) in checks.items()},
            }
            self.training.history.append(record)
            files.save_training(self.folder, self.training)
        return Report(self.training.generation, record["best"], record["mean"], checks, self.training.worlds)

    def check(self) -> Check:
        """Check the brain: for each ship, the share of levels it clears (one life each) and how far into them it gets.

        Opens the next world when the brain gets far enough into the open ones.
        """
        weights, hidden = self.brain.weights, self.brain.hidden
        count = len(_levels())
        tasks = [(weights, hidden, ship, index, index) for ship in self.ships for index in range(count)]
        results = list(self.executor.map(check_level, tasks))
        per_ship = {ship: results[number * count : (number + 1) * count] for number, ship in enumerate(self.ships)}
        opened = open_levels(self.training.worlds)
        reached = np.mean([gone for runs in per_ship.values() for _, gone in runs[:opened]])
        if self.training.worlds < len(_world_sizes()) and reached >= OPEN_NEXT:
            self.training.worlds += 1
        return {
            ship: (float(np.mean([cleared for cleared, _ in runs])), float(np.mean([gone for _, gone in runs])))
            for ship, runs in per_ship.items()
        }

    def save(self) -> None:
        """Save the brain and its training's progress."""
        files.save_training(self.folder, self.training)


def learn(
    ships: Iterable[str],
    generations: int,
    folder: Path,
    workers: int | None = None,
    report: Callable[[Report], None] = print,
    stop: Callable[[], bool] = lambda: False,
    executor: Executor | None = None,
    on_brain: Callable[[Brain], None] = lambda _brain: None,
) -> None:
    """Train the brain with `ships` for `generations` more generations (0: until stopped).

    `on_brain` gets the brain after each generation.
    """
    with executor or ProcessPoolExecutor(max_workers=workers or default_workers()) as pool:
        learner = Learner(ships, folder, pool)
        done = 0
        try:
            while (not generations or done < generations) and not stop():
                report(learner.step())
                on_brain(learner.brain)
                done += 1
        finally:
            if done:
                learner.save()
