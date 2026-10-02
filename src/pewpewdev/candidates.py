"""The model candidates: drawings for possible new enemies and bosses made by the tools.

Made by tools/candidates/ and tools/boss_candidates/, kept with the game's models but not in the game: the Enemy
candidates and Boss candidates screens show them.
"""

from pewpy.data import data_folder, read_yaml
from pewpy.graphics.models import DRAWINGS_FOLDER

CANDIDATES_FOLDER = "candidates"  # models/candidates/<number>.yaml: drawings for possible new enemies
# models/boss_candidates/<number>.yaml: possible new bosses' cores, with <number>_a.yaml... their parts' drawings and
# <number>.parts.yaml where the parts go (see tools/boss_candidates/).
BOSS_CANDIDATES_FOLDER = "boss_candidates"


def candidate_names() -> list[str]:
    """Return the model candidates' drawings, like "candidates/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    files = sorted(entry.name for entry in folder.iterdir() if entry.name.endswith(".yaml"))
    return [f"{CANDIDATES_FOLDER}/{name.removesuffix('.yaml')}" for name in files]


def boss_candidate_names() -> list[str]:
    """Return the boss candidates' cores, like "boss_candidates/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / BOSS_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    numbers = sorted(entry.name.removesuffix(".yaml") for entry in folder.iterdir() if entry.name.endswith(".yaml"))
    return [f"{BOSS_CANDIDATES_FOLDER}/{number}" for number in numbers if number.isdigit()]


def boss_candidate_parts(name: str) -> list[tuple[str, float, float]]:
    """Return a boss candidate's parts: (drawing, x, y), in cubes from the core's middle (x right, y up the screen)."""
    path = data_folder() / DRAWINGS_FOLDER / f"{name}.parts.yaml"
    if not path.is_file():
        return []
    folder = name.rsplit("/", 1)[0]
    layout = read_yaml(path)
    return [(f"{folder}/{entry['drawing']}", float(entry["x"]), float(entry["y"])) for entry in layout["parts"]]
