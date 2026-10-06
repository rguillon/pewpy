"""The candidates: drawings for possible new enemies and bosses, and possible new props, made by the tools.

Made by pewpy.tools.candidates, pewpy.tools.player_candidates, pewpy.tools.boss_candidates and
pewpy.tools.generate_props, kept in data/models/candidates/ (enemies/, player/, bosses/, props/) but not in the game:
the Enemy candidates, Player candidates, Boss candidates and Prop candidates screens show them.
"""

import json

from pewpy.data import data_folder
from pewpy.graphics.models import DRAWINGS_FOLDER
from pewpy.scenery.ground.props.model import PropModel

CANDIDATES_FOLDER = "candidates/enemies"  # models/candidates/enemies/<number>.json: drawings for possible new enemies
PLAYER_CANDIDATES_FOLDER = "candidates/player"  # models/candidates/player/<number>.json: possible new player ships
# models/candidates/bosses/<number>.json: possible new bosses' cores, with <number>_a.json... their parts' drawings
# and <number>.parts.json where the parts go (see pewpy.tools.boss_candidates).
BOSS_CANDIDATES_FOLDER = "candidates/bosses"
PROP_CANDIDATES_FOLDER = "candidates/props"  # models/candidates/props/<number>.json: possible new props


def candidate_names() -> list[str]:
    """Return the model candidates' drawings, like "candidates/enemies/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    files = sorted(entry.name for entry in folder.iterdir() if entry.name.endswith(".json"))
    return [f"{CANDIDATES_FOLDER}/{name.removesuffix('.json')}" for name in files]


def player_candidate_names() -> list[str]:
    """Return the player ship candidates' drawings, like "candidates/player/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / PLAYER_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    files = sorted(entry.name for entry in folder.iterdir() if entry.name.endswith(".json"))
    return [f"{PLAYER_CANDIDATES_FOLDER}/{name.removesuffix('.json')}" for name in files]


def boss_candidate_names() -> list[str]:
    """Return the boss candidates' cores, like "candidates/bosses/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / BOSS_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    numbers = sorted(entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json"))
    return [f"{BOSS_CANDIDATES_FOLDER}/{number}" for number in numbers if number.isdigit()]


def boss_candidate_parts(name: str) -> list[tuple[str, float, float]]:
    """Return a boss candidate's parts: (drawing, x, y), in cubes from the core's middle (x right, y up the screen)."""
    path = data_folder() / DRAWINGS_FOLDER / f"{name}.parts.json"
    if not path.is_file():
        return []
    folder = name.rsplit("/", 1)[0]
    layout = json.loads(path.read_text())
    return [(f"{folder}/{entry['drawing']}", float(entry["x"]), float(entry["y"])) for entry in layout["parts"]]


def prop_candidate_names() -> list[str]:
    """Return the prop candidates, like "001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / PROP_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    return sorted(entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json"))


def prop_candidate(name: str) -> PropModel:
    """Return a prop candidate, read again every time (edited files show when the page is shown again)."""
    path = data_folder() / DRAWINGS_FOLDER / PROP_CANDIDATES_FOLDER / f"{name}.json"
    return PropModel(name, json.loads(path.read_text()))
