"""Where the tools write: the game's source tree (its data files are made here), and the repository's build folder."""

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]  # src/pewpewdev/paths.py: two folders up
GAME = REPOSITORY / "src" / "pewpy"  # the game's package: its levels, models and music
BUILD = REPOSITORY / "build"
