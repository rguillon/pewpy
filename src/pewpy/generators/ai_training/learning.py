"""Teaching the brain to play every level with every ship, by evolution strategies (evolution.py).

One brain flies all the ships, seeing which one it flies (sensors.py).

Each generation, every try of the population plays the same runs, RUNS_PER_SHIP per ship, each on a level drawn
among the worlds open to it, with one life; its fitness is the mean of its runs' (episode.py). The tries play in
worker processes, in parallel. Every CHECK_EVERY generations the brain itself plays every level once with each ship:
the share it clears and how far it gets are its progress. It is kept if its grade (the share of runs it clears
times its mean score: it must survive and score) is as good as the best brain's so far, else training goes back to
that one: the training's noise can't undo what it learned. The best brain is saved (files.py), so learning can stop
at any time and go on later.

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
RUNS_PER_SHIP = 2  # each try's runs per ship, every generation
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


def try_weights(task: tuple[np.ndarray, tuple[int, ...], tuple[Run, ...]]) -> tuple[float, float]:
    """Play some runs with a brain's weights (in a worker process): its mean fitness, the share of runs cleared."""
    weights, hidden, runs = task
    brain = Brain(weights, hidden)
    levels = _levels()
    outcomes = [play(levels[index], brain, ship, seed) for ship, index, seed in runs]
    return float(np.mean([outcome.fitness for outcome in outcomes])), float(np.mean([o.cleared for o in outcomes]))


def check_level(task: tuple[np.ndarray, tuple[int, ...], str, int, int]) -> tuple[bool, float, int]:
    """Whether a brain clears a level with one life, how far it gets (from 0 to 1: the boss destroyed), its score."""
    weights, hidden, ship, index, seed = task
    outcome = play(_levels()[index], Brain(weights, hidden), ship, seed)
    return outcome.cleared, outcome.progress / 2, outcome.score


def default_workers() -> int:
    """Return how many worker processes to use: the cores but one."""
    return max(1, (os.cpu_count() or 2) - 1)


Check = dict[str, tuple[float, float]]  # for each ship: the share of levels the brain clears, how far it gets (0 to 1)
Plays = dict[str, list[tuple[bool, float, int]]]  # for each ship, its check's runs: cleared, how far it got, score


def summary(plays: Plays) -> Check:
    """For each ship: the share of its check's runs cleared and how far it got on average."""
    return {
        ship: (float(np.mean([cleared for cleared, _, _ in runs])), float(np.mean([gone for _, gone, _ in runs])))
        for ship, runs in plays.items()
    }


def mean_score(plays: Plays) -> float:
    """Return a check's mean score (every ship's runs)."""
    return float(np.mean([score for runs in plays.values() for _, _, score in runs]))


def grade(plays: Plays) -> float:
    """Grade a check, to compare brains: the share of its runs cleared times their mean score.

    A brain must both survive and score: clearing a tenth fewer runs costs as much as scoring a tenth less.
    """
    cleared = float(np.mean([won for runs in plays.values() for won, _, _ in runs]))
    return cleared * mean_score(plays)


@dataclass(frozen=True)
class Report:
    """How a generation went."""

    generation: int
    best: float  # the best try's fitness
    mean: float
    won: float = 0.0  # the share of the generation's runs cleared (every try's)
    checks: Check | None = None  # when the brain was checked this generation
    worlds: int = 1  # the worlds it trains on
    levels: int = 0  # how many levels it trains on, when they are given (no curriculum)
    kept: bool = True  # at a check: whether the brain graded as well as the best so far (else training went back to it)
    score: float = 0.0  # at a check: the brain's mean score
    grade: float = 0.0  # at a check: the brain's grade (the share of runs cleared times the mean score)
    top: float = 0.0  # at a check: the best brain's grade (after the check)


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
        """Train the `ships` given on the `levels` given, resuming the brain saved in `folder`."""
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
        self.trainee = self.training.brain  # the brain being trained; self.training.brain is the best one checked
        self.best: float | None = None  # the best brain's grade (checked again when learning starts)

    @property
    def brain(self) -> Brain:
        """Return the best brain so far (the one saved)."""
        return self.training.brain

    def step(self) -> Report:
        """Play a generation: every try plays the runs, the evolution steps; check the brain every CHECK_EVERY."""
        levels = self.levels or tuple(range(open_levels(self.training.worlds)))
        runs = tuple(
            (ship, self.rng.choice(levels), self.rng.randrange(1_000_000))
            for ship in self.ships
            for _ in range(RUNS_PER_SHIP)
        )
        nudges, tries = self.evolution.ask()
        hidden = self.trainee.hidden
        results = np.array(list(self.executor.map(try_weights, [(w, hidden, runs) for w in tries])))
        fitness, won = results[:, 0], float(results[:, 1].mean())
        self.evolution.tell(nudges, fitness)
        self.trainee = Brain(self.evolution.weights.copy(), hidden)
        self.training.generation = self.evolution.generation
        checks = None
        kept, score, graded = True, 0.0, 0.0
        record: dict[str, Any] = {
            "generation": self.training.generation,
            "best": float(fitness.max()),
            "mean": float(fitness.mean()),
            "won": won,
        }
        if self.training.generation % CHECK_EVERY == 0:
            checks, score, graded, kept = self.check()
            record |= {
                "cleared": float(np.mean([cleared for cleared, _ in checks.values()])),
                "progress": float(np.mean([gone for _, gone in checks.values()])),
                "score": score,
                "grade": graded,
                "kept": kept,
                "worlds": self.training.worlds,
                **({"levels": len(self.levels)} if self.levels else {}),
                "ships": {ship: {"cleared": cleared, "progress": gone} for ship, (cleared, gone) in checks.items()},
            }
            self.training.history.append(record)
            files.save_training(self.folder, self.training)
        trained = len(self.levels) if self.levels else 0
        top = self.best or 0.0
        return Report(
            self.training.generation,
            record["best"],
            record["mean"],
            won=won,
            checks=checks,
            worlds=self.training.worlds,
            levels=trained,
            kept=kept,
            score=score,
            grade=graded,
            top=top,
        )

    def check(self) -> tuple[Check, float, float, bool]:
        """Check the brain being trained: keep it if it grades as well as the best so far, else go back to that one.

        Its check, its mean score, its grade and whether it was kept. A kept brain may open the next world (the
        curriculum).
        """
        if self.best is None:
            self.best = grade(self.play_checks(self.training.brain))
        plays = self.play_checks(self.trainee)
        graded = grade(plays)
        kept = graded >= self.best
        if kept:
            self.training.brain, self.best = self.trainee, graded
            self.open_worlds(plays)
        else:  # it got worse (or was unlucky): its training's last steps are dropped
            self.trainee = self.training.brain
            self.evolution.restart(self.trainee.weights)
        return summary(plays), mean_score(plays), graded, kept

    def play_checks(self, brain: Brain) -> Plays:
        """For each ship, how a brain does on its check, with one life each and the same randomness every check.

        Every level once; or the levels given, CHECK_RUNS runs in all.
        """
        if self.levels:
            repeats = -(-CHECK_RUNS // len(self.levels))
            plays = [(index, run) for index in self.levels for run in range(repeats)]
        else:
            plays = [(index, index) for index in range(len(_levels()))]
        tasks = [(brain.weights, brain.hidden, ship, index, seed) for ship in self.ships for index, seed in plays]
        results = list(self.executor.map(check_level, tasks))
        return {ship: results[n * len(plays) : (n + 1) * len(plays)] for n, ship in enumerate(self.ships)}

    def open_worlds(self, plays: Plays) -> None:
        """Open the next world once the brain gets far enough into the open ones (with the curriculum)."""
        if self.levels:
            return
        opened = open_levels(self.training.worlds)
        reached = np.mean([gone for runs in plays.values() for _, gone, _ in runs[:opened]])
        if self.training.worlds < len(_world_sizes()) and reached >= OPEN_NEXT:
            self.training.worlds += 1

    def save(self) -> None:
        """Save the best brain and its training's progress."""
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
