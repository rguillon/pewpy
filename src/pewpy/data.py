"""Where the game's data files are (levels, model drawings).

Normally inside the installed `pewpy` package. In a packaged build (Panda3D's build_apps, see `make package`) the
code is frozen into the executable, so the data files are copied to a `pewpy` folder next to it instead.
"""

import sys
from importlib import resources
from pathlib import Path

if sys.version_info >= (3, 11):
    from importlib.resources.abc import Traversable
else:  # pragma: no cover - where Python 3.10 keeps it
    from importlib.abc import Traversable


def data_folder() -> Traversable:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "pewpy"
    return resources.files("pewpy")
