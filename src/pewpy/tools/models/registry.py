"""What a recipe is, and where the models go."""

import os
from collections.abc import Callable
from pathlib import Path

from pewpy.data import model_path
from pewpy.tools.models.sculpt import Model

Recipe = Callable[[], tuple[Model, list[dict] | None]]
SCALE = int(os.environ.get("MODELS_SCALE", "2"))  # cubes per unit (config.MODEL_VOXEL)


def model_file(name: str, suffix: str = ".json") -> Path:
    """Return a model's file, wherever it is in data/models/ (see pewpy.data.model_path), or the .vox next to it."""
    return Path(str(model_path(name))).with_suffix(suffix)
