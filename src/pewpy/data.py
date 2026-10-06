"""Where the game's data files are: the `data/` folder at the top of the project.

It holds the rules, ships, weapons, enemies, bosses, levels, models, music and the font. The models are in
`models/<group>/<name>.json` (MODEL_GROUPS: the enemies', the bosses' (cores and parts), the player's ships and missile,
the items: the pickups), the props in `models/props/`, the tools' candidates in `models/candidates/` (not in the
game). A model's name is unique across the groups, so the game data names a model without its group. An installed wheel
carries it inside the `pewpy` package (`pewpy/data`, see pyproject.toml). In a packaged build (Panda3D's build_apps,
see `make package`) the code is frozen into the executable, and the data files are copied to a `data` folder next to
it.
"""

import sys
from functools import cache
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # only for the type checker
    from importlib.resources.abc import Traversable

SOURCE_DATA = Path(__file__).resolve().parents[2] / "data"  # src/pewpy/data.py: two folders up, then data/


def data_folder() -> "Traversable":
    """Return the folder of the game's data files."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "data"
    bundled = resources.files("pewpy") / "data"
    return bundled if bundled.is_dir() else SOURCE_DATA


MODELS_FOLDER = "models"  # data/models/
MODEL_GROUPS = ("enemies", "bosses", "player", "items")  # data/models/<group>/: where the game's models are


def model_folder(name: str) -> str:
    """Return the folder of a model, within models/: its group for a name alone, else the folder in its name.

    "drone" is in "enemies"; "candidates/bosses/007_a" in "candidates/bosses". A name in no group: "".
    """
    if "/" in name:
        return name.rsplit("/", 1)[0]
    return _groups(str(data_folder())).get(name, "")


def model_path(name: str) -> "Traversable":
    """Return the file of a model (see `model_folder`): models/<folder>/<name>.json."""
    folder = data_folder() / MODELS_FOLDER
    group = model_folder(name)
    file = f"{name.rsplit('/', 1)[-1]}.json"
    return folder / group / file if group else folder / file


@cache
def _groups(root: str) -> dict[str, str]:
    """Return each model's group, in the data folder `root` (looked through once: tests have folders of their own)."""
    groups: dict[str, str] = {}
    for group in MODEL_GROUPS:
        folder = Path(root) / MODELS_FOLDER / group
        if folder.is_dir():
            names = (entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json"))
            groups.update(dict.fromkeys(names, group))
    return groups
