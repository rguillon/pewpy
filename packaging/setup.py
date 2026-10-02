"""Panda3D's build_apps settings for `make package`: a standalone Windows build of the game.

Run from the repository's root (the patterns below are relative to it). The code is frozen into `pewpy.exe`; the
data files (weapons, enemies, bosses, levels, model drawings) are copied to a `pewpy` folder next to it (see pewpy/data.py). The Windows
wheels of the dependencies (build/requirements.txt, exported from uv.lock) are downloaded, so this runs on any OS.
"""

import pkgutil
from importlib import metadata

import numpy
from setuptools import setup

# build_apps finds the modules to freeze by reading imports in Python code, but numpy's compiled core imports some
# of its own Python modules, and Panda3D's list of those still has numpy 1's names (numpy.core): include every
# module of numpy 2's core (numpy._core), except its tests.
NUMPY_CORE = [
    module.name
    for module in pkgutil.iter_modules(numpy._core.__path__, "numpy._core.")
    if not module.name.endswith("_tests") and not module.name.split(".")[-1].startswith("test")
]

setup(
    name="pewpy",
    version=metadata.version("pewpy"),  # from pyproject.toml, the project being installed in the environment
    options={
        "build_apps": {
            "gui_apps": {"pewpy": "src/pewpy/__main__.py"},
            "platforms": ["win_amd64"],
            "plugins": ["pandagl", "p3openal_audio"],
            "include_patterns": [
                "src/pewpy/bosses/*.json",
                "src/pewpy/enemies/*.json",
                "src/pewpy/weapons/*.json",
                "src/pewpy/levels/**/*.json",
                "src/pewpy/models/*.json",
                "src/pewpy/models/*.vox",
                "src/pewpy/music/*.mid",
            ],
            "rename_paths": {"src/pewpy/": "pewpy/"},
            "exclude_patterns": [".venv/**", ".git/**", "build/**", "dist/**", "site/**", "tests/**", "docs/**"],
            "requirements_path": "build/requirements.txt",
            "include_modules": {"*": NUMPY_CORE},
            "build_base": "build/package",
            # A windowed game has no console: errors go to %LOCALAPPDATA%\\pewpy\\output.log instead.
            "log_filename": "$USER_APPDATA/pewpy/output.log",
            "log_append": False,
        },
        "bdist_apps": {"installers": {"win_amd64": ["zip"]}, "dist_dir": "dist"},
    },
)
