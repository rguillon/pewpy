"""What a recipe is, and where the models go."""

import os
from collections.abc import Callable
from pathlib import Path

from pewpy.data import model_path, split_model_name
from pewpy.tools.models.sculpt import Model

Recipe = Callable[[], tuple[Model, list[dict] | None]]
SCALE = int(os.environ.get("MODELS_SCALE", "2"))  # cubes per unit (config.MODEL_VOXEL)


def model_file(name: str, suffix: str = ".json") -> Path:
    """Return a model's file, wherever it is in data/models/ (see pewpy.data.model_path), or the .vox next to it.

    A part ("avalanche:a") is in its model's file; its .vox is its own ("avalanche_a.vox").
    """
    path = Path(str(model_path(name)))
    part = split_model_name(name)[1]
    if suffix == ".json" or not part:
        return path.with_suffix(suffix)
    return path.with_name(f"{path.stem}_{part}{suffix}")
