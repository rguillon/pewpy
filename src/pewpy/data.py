"""Where the game's data files are: the `data/` folder at the top of the project.

It holds the rules, ships, weapons, enemies, bosses, levels, model drawings, music and the font. An installed wheel
carries it inside the `pewpy` package (`pewpy/data`, see pyproject.toml). In a packaged build (Panda3D's build_apps,
see `make package`) the code is frozen into the executable, and the data files are copied to a `data` folder next to
it.
"""

import sys
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:  # only for the type checker
    from importlib.resources.abc import Traversable

_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)  # libyaml's, much faster, when PyYAML has it

SOURCE_DATA = Path(__file__).resolve().parents[2] / "data"  # src/pewpy/data.py: two folders up, then data/


def data_folder() -> "Traversable":
    """Return the folder of the game's data files."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "data"
    bundled = resources.files("pewpy") / "data"
    return bundled if bundled.is_dir() else SOURCE_DATA


def read_yaml(file: "Traversable") -> Any:  # noqa: ANN401 (whatever the file holds)
    """Read a YAML file."""
    return parse_yaml(file.read_text())


def parse_yaml(text: str) -> Any:  # noqa: ANN401 (whatever the text holds)
    """Decode YAML text."""
    return yaml.load(text, Loader=_LOADER)  # noqa: S506 (a safe loader)
