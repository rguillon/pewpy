r"""Where the AI keeps what it learned.

One brain for every ship (`brain.npz`, with its training's progress) and the levels' ratings (`ratings.json`), in the
user's data folder (~/.local/share/pewpy/ai, %LOCALAPPDATA%\pewpy\ai on Windows).
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from pewpewdev.ai import sensors
from pewpewdev.ai.brain import Brain


def ai_folder() -> Path:
    """Return the folder the AI keeps its files in, in the user's data folder."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "pewpy" / "ai"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "pewpy" / "ai"


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
        if int(data["inputs"]) != sensors.SIZE:
            return None  # made for sensors that have changed since: it would see nonsense
        brain = Brain(data["weights"], tuple(int(n) for n in data["hidden"]), int(data["inputs"]))
        worlds = int(data["worlds"]) if "worlds" in data else 1
        return Training(brain, int(data["generation"]), json.loads(str(data["history"])), worlds)


def save_ratings(folder: Path, ratings: dict[str, Any]) -> Path:
    """Write the levels' ratings; return where they went."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "ratings.json"
    path.write_text(json.dumps(ratings, indent=2) + "\n")
    return path


def load_ratings(folder: Path) -> dict[str, Any] | None:
    """Read the levels' ratings, or None if there are none yet."""
    path = folder / "ratings.json"
    return json.loads(path.read_text()) if path.exists() else None
