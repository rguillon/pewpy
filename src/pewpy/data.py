"""Where the game's data files are: the `data/` folder at the top of the project.

It holds the rules, ships, weapons, enemies, bosses, levels, model drawings and music. An installed wheel carries it
inside the `pewpy` package (`pewpy/data`, see pyproject.toml). In a packaged build (Panda3D's build_apps, see `make
package`) the code is frozen into the executable, and the data files are copied to a `data` folder next to it.
"""

import sys
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # only for the type checker: where it lives depends on the Python version
    if sys.version_info >= (3, 11):
        from importlib.resources.abc import Traversable
    else:
        from importlib.abc import Traversable

SOURCE_DATA = Path(__file__).resolve().parents[2] / "data"  # src/pewpy/data.py: two folders up, then data/


def data_folder() -> "Traversable":
    """Return the folder of the game's data files."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "data"
    bundled = resources.files("pewpy") / "data"
    return bundled if bundled.is_dir() else SOURCE_DATA
