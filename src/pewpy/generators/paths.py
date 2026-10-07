"""Where the command line tools write: the game's data folder (data/, its files are made here)."""

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[3]  # src/pewpy/generators/paths.py: three folders up
DATA = REPOSITORY / "data"  # the game's data files: its levels, models, bosses, music...
