"""The model candidates, drawings for possible new enemies and bosses made by the tools (make_candidates.py,
make_boss_candidates.py), kept with the game's models but not in the game: the Enemy candidates and Boss candidates
screens show them.
"""

import json

from pewpy.data import data_folder
from pewpy.graphics.models import DRAWINGS_FOLDER

CANDIDATES_FOLDER = "candidates"  # models/candidates/<number>.json: drawings for possible new enemies
# models/boss_candidates/<number>.json: possible new bosses' cores, with <number>_a.json... their parts' drawings and
# <number>.parts.json where the parts go (see tools/make_boss_candidates.py).
BOSS_CANDIDATES_FOLDER = "boss_candidates"


def candidate_names() -> list[str]:
    """The model candidates' drawings, like "candidates/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    files = sorted(entry.name for entry in folder.iterdir() if entry.name.endswith(".json"))
    return [f"{CANDIDATES_FOLDER}/{name.removesuffix('.json')}" for name in files]


def boss_candidate_names() -> list[str]:
    """The boss candidates' cores, like "boss_candidates/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / BOSS_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    numbers = sorted(entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json"))
    return [f"{BOSS_CANDIDATES_FOLDER}/{number}" for number in numbers if number.isdigit()]


def boss_candidate_parts(name: str) -> list[tuple[str, float, float]]:
    """A boss candidate's parts: (drawing, x, y), in cubes from the core's middle (x right, y up the screen)."""
    path = data_folder() / DRAWINGS_FOLDER / f"{name}.parts.json"
    if not path.is_file():
        return []
    folder = name.rsplit("/", 1)[0]
    layout = json.loads(path.read_text())
    return [(f"{folder}/{entry['drawing']}", float(entry["x"]), float(entry["y"])) for entry in layout["parts"]]
