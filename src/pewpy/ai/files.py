"""Where the AI keeps what it learned: one brain for every ship, with its training's progress.

In the game's data folder, `brain/brain.npz` (data/brain/ in the project: the learning tools write it there, and the
game ships with it).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from pewpy.ai import sensors
from pewpy.ai.brain import Brain, parameter_count
from pewpy.data import data_folder

BRAIN_FOLDER = "brain"  # in the game's data folder


def brain_folder() -> Path:
    """Return the folder the brain is kept in, in the game's data folder."""
    return Path(str(data_folder() / BRAIN_FOLDER))


@dataclass
class Training:
    """The brain and how its training went.

    Every CHECK_EVERY generations: the best try's fitness, the share of levels it cleared and how far it got with each
    ship; and how many worlds it trains on so far (learning.py).
    """

    brain: Brain
    generation: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    worlds: int = 1


def brain_path(folder: Path) -> Path:
    """Return where the brain is kept in `folder`."""
    return folder / "brain.npz"


def save_training(folder: Path, training: Training) -> None:
    """Save the brain and its training's progress (through a temporary file, so a crash leaves the old one)."""
    folder.mkdir(parents=True, exist_ok=True)
    path = brain_path(folder)
    temporary = path.with_suffix(".tmp.npz")
    np.savez(
        temporary,
        weights=training.brain.weights,
        hidden=np.array(training.brain.hidden),
        inputs=np.array(training.brain.inputs),
        generation=np.array(training.generation),
        worlds=np.array(training.worlds),
        history=np.array(json.dumps(training.history)),
    )
    temporary.replace(path)  # never a half-written brain, even if the game is closed while saving


def load_training(folder: Path) -> Training | None:
    """Load the brain, or None if there is none yet (or one made for other sensors)."""
    path = brain_path(folder)
    if not path.exists():
        return None
    with np.load(path) as data:
        hidden = tuple(int(n) for n in data["hidden"])
        if int(data["inputs"]) != sensors.SIZE or len(data["weights"]) != parameter_count(sensors.SIZE, hidden):
            return None  # made for other sensors or outputs: it would see or do nonsense
        brain = Brain(data["weights"], hidden, int(data["inputs"]))
        worlds = int(data["worlds"]) if "worlds" in data else 1
        return Training(brain, int(data["generation"]), json.loads(str(data["history"])), worlds)
