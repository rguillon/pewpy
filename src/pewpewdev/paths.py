"""Where the tools write: the game's data folder (data/, its files are made here), and the repository's build folder."""

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]  # src/pewpewdev/paths.py: two folders up
DATA = REPOSITORY / "data"  # the game's data files: its levels, models, bosses, music...
BUILD = REPOSITORY / "build"
