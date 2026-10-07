"""Where the tools write: the game's data folder (data/, its files are made here)."""

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[3]  # src/pewpy/tools/paths.py: three folders up
DATA = REPOSITORY / "data"  # the game's data files: its levels, models, bosses, music...
