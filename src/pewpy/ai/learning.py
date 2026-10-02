"""Teaching a ship's brain to play every level, by evolution strategies (evolution.py).

Each generation, every try of the population plays the same LEVELS_PER_TRY levels, drawn among the worlds open to
it, with one life each; its fitness is the mean of its runs' (episode.py). The tries play in worker processes, in
parallel. Every CHECK_EVERY generations the brain itself plays every level once: the share it clears and how far it
gets are its progress, and it is saved (files.py), so learning can stop at any time and go on later.

A curriculum: a new brain trains on world 1 only; the next world opens once it gets OPEN_NEXT of the way into the
open worlds' levels on average at a check.
"""

import os
import random
from collections.abc import Callable, Iterable
from concurrent.futures import Executor, ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import numpy as np

from pewpy.ai import files
from pewpy.ai.brain import HIDDEN, Brain
from pewpy.ai.episode import play
from pewpy.ai.evolution import Evolution
from pewpy.game.level import Level, load_levels, load_worlds

LEVELS_PER_TRY = 3
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


def try_weights(task: tuple[np.ndarray, tuple[int, ...], str, tuple[tuple[int, int], ...]]) -> float:
    """Play some levels with a brain's weights (in a worker process): its mean fitness."""
    weights, hidden, ship, runs = task
    brain = Brain(weights, hidden)
    levels = _levels()
    return float(np.mean([play(levels[index], brain, ship, seed).fitness for index, seed in runs]))


def check_level(task: tuple[np.ndarray, tuple[int, ...], str, int, int]) -> tuple[bool, float]:
    """Whether a brain clears a level with one life, and how far it gets (from 0 to 1: the boss destroyed)."""
    weights, hidden, ship, index, seed = task
    outcome = play(_levels()[index], Brain(weights, hidden), ship, seed)
    return outcome.cleared, outcome.progress / 2


def default_workers() -> int:
    return max(1, (os.cpu_count() or 2) - 1)


@dataclass(frozen=True)
class Report:
    ship: str
    generation: int
    best: float  # the best try's fitness
    mean: float
    cleared: float | None  # the share of levels the brain clears, when it was checked this generation...
    progress: float | None = None  # ...and how far into them it gets on average, from 0 to 1
    worlds: int = 1  # the worlds it trains on


class Learner:
    """One ship's training, a generation at a time."""

    def __init__(self, ship: str, folder: Path, executor: Executor, seed: int = 0) -> None:
        self.ship = ship
        self.folder = folder
        self.executor = executor
        saved = files.load_training(folder, ship)
        self.training = saved or files.Training(Brain.random(np.random.default_rng(seed), HIDDEN))
        # Levels to play, not cryptography; a resumed training draws new ones, not the start's again.
        self.rng = random.Random(seed * 1_000_003 + self.training.generation)  # noqa: S311
        self.evolution = Evolution(
            self.training.brain.weights.copy(), np.random.default_rng(seed + self.training.generation)
        )
        self.evolution.generation = self.training.generation

    @property
    def brain(self) -> Brain:
        return self.training.brain

    def step(self) -> Report:
        levels = open_levels(self.training.worlds)
        runs = tuple((self.rng.randrange(levels), self.rng.randrange(1_000_000)) for _ in range(LEVELS_PER_TRY))
        nudges, tries = self.evolution.ask()
        hidden = self.brain.hidden
        fitness = np.array(list(self.executor.map(try_weights, [(w, hidden, self.ship, runs) for w in tries])))
        self.evolution.tell(nudges, fitness)
        self.training.brain = Brain(self.evolution.weights.copy(), hidden)
        self.training.generation = self.evolution.generation
        cleared = progress = None
        record = {"generation": self.training.generation, "best": float(fitness.max()), "mean": float(fitness.mean())}
        if self.training.generation % CHECK_EVERY == 0:
            cleared, progress = self.check()
            record |= {"cleared": cleared, "progress": progress, "worlds": self.training.worlds}
            self.training.history.append(record)
            files.save_training(self.folder, self.ship, self.training)
        return Report(
            self.ship, self.training.generation, record["best"], record["mean"], cleared, progress, self.training.worlds
        )

    def check(self) -> tuple[float, float]:
        """The share of levels the brain clears (one life each), and how far into them it gets on average; opens
        the next world when it gets far enough into the open ones."""
        weights, hidden = self.brain.weights, self.brain.hidden
        tasks = [(weights, hidden, self.ship, index, index) for index in range(len(_levels()))]
        results = list(self.executor.map(check_level, tasks))
        opened = open_levels(self.training.worlds)
        if self.training.worlds < len(_world_sizes()) and np.mean([gone for _, gone in results[:opened]]) >= OPEN_NEXT:
            self.training.worlds += 1
        return float(np.mean([cleared for cleared, _ in results])), float(np.mean([gone for _, gone in results]))

    def save(self) -> None:
        files.save_training(self.folder, self.ship, self.training)


def learn(
    ships: Iterable[str],
    generations: int,
    folder: Path,
    workers: int | None = None,
    report: Callable[[Report], None] = print,
    stop: Callable[[], bool] = lambda: False,
    executor: Executor | None = None,
    on_brain: Callable[[str, Brain], None] = lambda ship, brain: None,
) -> None:
    """Train each ship's brain for `generations` more generations (0: until stopped), the ships taking turns every
    CHECK_EVERY; `on_brain` gets each ship's brain after each generation."""
    with executor or ProcessPoolExecutor(max_workers=workers or default_workers()) as pool:
        learners = [Learner(ship, folder, pool, seed=index) for index, ship in enumerate(ships)]
        done = 0
        while (not generations or done < generations) and not stop():
            turn = CHECK_EVERY if not generations else min(CHECK_EVERY, generations - done)
            for learner in learners:
                stepped = False
                for _ in range(turn):
                    if stop():
                        break
                    report(learner.step())
                    on_brain(learner.ship, learner.brain)
                    stepped = True
                if stepped:
                    learner.save()
                if stop():
                    return
            done += turn
