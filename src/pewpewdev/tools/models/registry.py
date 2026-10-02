"""What a recipe is, and where the models go."""

import os
from collections.abc import Callable

from pewpewdev.paths import DATA
from pewpewdev.tools.models.sculpt import Model

MODELS = DATA / "models"
Recipe = Callable[[], tuple[Model, list[dict] | None]]
SCALE = int(os.environ.get("MODELS_SCALE", "2"))  # cubes per unit (config.MODEL_VOXEL)
