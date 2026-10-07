"""Teaching the brain to play every level with every ship, by evolution strategies (evolution.py).

One brain flies all the ships, seeing which one it flies (sensors.py).

Each generation, every try of the population plays the same runs, one per ship, each on a level drawn among the
worlds open to it, with one life; its fitness is the mean of its runs' (episode.py). The tries play in worker
processes, in parallel. Every CHECK_EVERY generations the brain itself plays every level once with each ship: the
share it clears and how far it gets are its progress, and it is saved (files.py), so learning can stop at any time
and go on later.

A curriculum: a new brain trains on world 1 only; the next world opens once it gets OPEN_NEXT of the way into the
open worlds' levels on average (every ship's) at a check. Or no curriculum: training on the levels given (`make
learn-level1`: the first one; `make learn-random`: all of them), each check playing them CHECK_RUNS times in all
with each ship.
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

from pewpy.ai import files
from pewpy.ai.brain import HIDDEN, Brain
from pewpy.game.level import Level, load_levels, load_worlds
from pewpy.generators.ai_training.episode import play
from pewpy.generators.ai_training.evolution import Evolution

CHECK_EVERY = 10  # generations
CHECK_RUNS = 48  # runs per ship at a check on the levels given (each level as often, at least once)
OPEN_NEXT = 0.5  # how far into the open worlds' levels (on average, 0.5: the final boss) for the next world to open


@cache
def _levels() -> tuple[Level, ...]:
    return tuple(load_levels())


@cache
def _world_sizes() -> tuple[int, ...]:
    """How many levels each world has, in order (_levels() has them one world after the other)."""
    return tuple(len(world.levels) for world in load_worlds())


def level_index(place: str) -> int:
    """Return where the level at `place` ("2-5": world 2, level 5) is in _levels()."""
    world, _, number = place.partition("-")
    sizes = _world_sizes()
    if not (world.isdigit() and number.isdigit() and 1 <= int(world) <= len(sizes)):
        msg = f"no level {place} (levels are like 1-1)"
        raise ValueError(msg)
    if not 1 <= int(number) <= sizes[int(world) - 1]:
        msg = f"no level {place} (levels are like 1-1)"
        raise ValueError(msg)
    return sum(sizes[: int(world) - 1]) + int(number) - 1


def every_level() -> tuple[int, ...]:
    """Every level's index."""
    return tuple(range(len(_levels())))


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
    levels: int = 0  # how many levels it trains on, when they are given (no curriculum)


class Learner:
    """The brain's training, a generation at a time, with the `ships` given.

    On the `levels` given (their indexes), or with the curriculum; a `new` brain, or the saved one if there is one.
    """

    def __init__(
        self,
        ships: Iterable[str],
        folder: Path,
        executor: Executor,
        seed: int = 0,
        levels: tuple[int, ...] | None = None,
        new: bool = False,
    ) -> None:
        self.ships = list(ships)
        self.folder = folder
        self.executor = executor
        self.levels = levels
        saved = None if new else files.load_training(folder)
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
        levels = self.levels or tuple(range(open_levels(self.training.worlds)))
        runs = tuple((ship, self.rng.choice(levels), self.rng.randrange(1_000_000)) for ship in self.ships)
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
                **({"levels": len(self.levels)} if self.levels else {}),
                "ships": {ship: {"cleared": cleared, "progress": gone} for ship, (cleared, gone) in checks.items()},
            }
            self.training.history.append(record)
            files.save_training(self.folder, self.training)
        trained = len(self.levels) if self.levels else 0
        return Report(self.training.generation, record["best"], record["mean"], checks, self.training.worlds, trained)

    def check(self) -> Check:
        """Check the brain: for each ship, the share of levels it clears (one life each) and how far into them it gets.

        Every level once, opening the next world when the brain gets far enough into the open ones; or the levels
        given, CHECK_RUNS runs in all.
        """
        weights, hidden = self.brain.weights, self.brain.hidden
        if self.levels:
            repeats = -(-CHECK_RUNS // len(self.levels))
            plays = [(index, run) for index in self.levels for run in range(repeats)]
            tasks = [(weights, hidden, ship, index, run) for ship in self.ships for index, run in plays]
            results = list(self.executor.map(check_level, tasks))
            per_ship = {ship: results[n * len(plays) : (n + 1) * len(plays)] for n, ship in enumerate(self.ships)}
            return {
                ship: (float(np.mean([cleared for cleared, _ in runs])), float(np.mean([gone for _, gone in runs])))
                for ship, runs in per_ship.items()
            }
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
    levels: tuple[int, ...] | None = None,
    new: bool = False,
) -> None:
    """Train the brain with `ships` for `generations` more generations (0: until stopped).

    On the `levels` given (their indexes), else with the curriculum; a `new` brain replaces the saved one.
    """
    with ProcessPoolExecutor(max_workers=workers or default_workers()) as pool:
        learner = Learner(ships, folder, pool, levels=levels, new=new)
        done = 0
        try:
            while not generations or done < generations:
                report(learner.step())
                done += 1
        except KeyboardInterrupt:  # stopped (Ctrl+C): what it learned so far is kept
            if done:
                learner.save()
            raise
        learner.save()
