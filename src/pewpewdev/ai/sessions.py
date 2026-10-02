"""Learning and rating in the background while the game shows them (the AI learning and AI rating screens): each
runs in a thread of its own, its worker processes doing the playing; the game reads where it is at every frame.
"""

import threading
from collections.abc import Callable
from concurrent.futures import Executor
from pathlib import Path

from pewpewdev.ai import files
from pewpewdev.ai.brain import Brain
from pewpewdev.ai.learning import Check, Report, learn
from pewpewdev.ai.rating import Rating, rate


class Session:
    """A job in a thread, that can be asked to stop (it stops at the end of what it is doing)."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.stopping = threading.Event()
        self.error: str | None = None
        self.done = False
        self.thread = threading.Thread(target=self._run, name=type(self).__name__, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self, wait: float = 0.0) -> None:
        self.stopping.set()
        if wait and self.thread.is_alive():
            self.thread.join(wait)

    def _run(self) -> None:
        try:
            self.work()
        except Exception as error:
            self.error = f"{type(error).__name__}: {error}"
        finally:
            self.done = True

    def work(self) -> None:
        raise NotImplementedError


class LearningSession(Session):
    """The brain learning, with every ship, until stopped."""

    def __init__(
        self, ships: list[str], folder: Path, workers: int | None = None, executor: Executor | None = None
    ) -> None:
        super().__init__()
        self.ships, self.folder, self.workers, self.executor = ships, folder, workers, executor
        self.report: Report | None = None  # the last generation's
        self.checks: Check = {}  # the last check, for each ship: cleared, progress
        self.current: Brain | None = None
        training = files.load_training(folder)
        if training is not None:
            self.current = training.brain
            checks = [record for record in training.history if "ships" in record]
            if checks:
                self.checks = {ship: (r["cleared"], r["progress"]) for ship, r in checks[-1]["ships"].items()}

    def work(self) -> None:
        learn(
            self.ships,
            0,
            self.folder,
            self.workers,
            report=self._report,
            stop=self.stopping.is_set,
            executor=self.executor,
            on_brain=self._brain,
        )

    def _report(self, report: Report) -> None:
        with self.lock:
            self.report = report
            if report.checks is not None:
                self.checks = dict(report.checks)

    def _brain(self, brain: Brain) -> None:
        with self.lock:
            self.current = brain

    def brain(self) -> Brain | None:
        with self.lock:
            return self.current


class RatingSession(Session):
    """Every level rated for every ship with the brain (none without a brain)."""

    def __init__(
        self,
        ships: list[str],
        folder: Path,
        runs: int,
        workers: int | None = None,
        executor: Executor | None = None,
        on_rating: Callable[[str, Rating], None] = lambda ship, rating: None,
    ) -> None:
        super().__init__()
        self.folder, self.runs, self.workers, self.executor, self.on_rating = folder, runs, workers, executor, on_rating
        self.ships = ships if files.load_training(folder) is not None else []
        self.ratings: dict[str, list[Rating]] = {ship: [] for ship in self.ships}
        self.saved = False

    def work(self) -> None:
        if not self.ships:
            return
        rate(
            self.ships,
            self.folder,
            self.runs,
            self.workers,
            report=self._report,
            stop=self.stopping.is_set,
            executor=self.executor,
        )
        self.saved = not self.stopping.is_set()

    def _report(self, ship: str, rating: Rating) -> None:
        with self.lock:
            self.ratings[ship].append(rating)
        self.on_rating(ship, rating)

    def table(self) -> dict[str, list[Rating]]:
        with self.lock:
            return {ship: list(ratings) for ship, ratings in self.ratings.items()}
