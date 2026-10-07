"""Tiny levels to train on, and worker pools that run in this process, so training runs in an instant."""

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import Executor
from typing import Any

import pytest

from pewpy.ai.training import learning, winrate
from pewpy.game.level import Level, LevelWorld, Wave

EMPTY = Level(name="empty", scroll_speed=0.2, waves=())  # cleared at once
DRONES = Level(name="drones", scroll_speed=0.2, waves=(Wave(time=0.1, enemy="drone"),))
TINY_WORLDS = (LevelWorld("First", (EMPTY, EMPTY)), LevelWorld("Second", (EMPTY, DRONES)))


class InlinePool(Executor):
    """A worker pool playing in this process."""

    def __init__(self, max_workers: int | None = None) -> None:
        self.max_workers = max_workers

    def map(self, fn: Callable[..., Any], *iterables: Iterable[Any], **_: Any) -> Iterator[Any]:  # noqa: ANN401
        return map(fn, *iterables)


@pytest.fixture
def tiny_levels(monkeypatch: pytest.MonkeyPatch) -> tuple[LevelWorld, ...]:
    """Train on two worlds of two tiny levels each, in this process."""
    levels = tuple(level for world in TINY_WORLDS for level in world.levels)
    monkeypatch.setattr(learning, "_levels", lambda: levels)
    monkeypatch.setattr(learning, "_world_sizes", lambda: tuple(len(world.levels) for world in TINY_WORLDS))
    places = tuple(
        (f"{w}-{n}", level)
        for w, world in enumerate(TINY_WORLDS, start=1)
        for n, level in enumerate(world.levels, start=1)
    )
    monkeypatch.setattr(winrate, "places", lambda: places)
    monkeypatch.setattr(learning, "ProcessPoolExecutor", InlinePool)
    monkeypatch.setattr(winrate, "ProcessPoolExecutor", InlinePool)
    return TINY_WORLDS
