"""The candidates: drawings for possible new enemies and bosses, possible new props and backgrounds, made by the tools.

Made by pewpy.tools.candidates, pewpy.tools.player_candidates, pewpy.tools.boss_candidates,
pewpy.tools.generate_props and pewpy.tools.background_candidates, kept in data/models/candidates/ (enemies/, player/,
bosses/, props/, backgrounds/) but not in the game: the Enemy candidates, Player candidates, Boss candidates, Prop
candidates and Background candidates screens show them.
"""

import json

from pewpy.data import PART_SEPARATOR, data_folder, read_model
from pewpy.game.level import Level
from pewpy.graphics.models import DRAWINGS_FOLDER
from pewpy.scenery.ground.props.model import PropModel

CANDIDATES_FOLDER = "candidates/enemies"  # models/candidates/enemies/<number>.json: drawings for possible new enemies
PLAYER_CANDIDATES_FOLDER = "candidates/player"  # models/candidates/player/<number>.json: possible new player ships
# models/candidates/bosses/<number>.json: possible new bosses, each a core with its parts' drawings and where they go
# (see pewpy.tools.boss_candidates).
BOSS_CANDIDATES_FOLDER = "candidates/bosses"
PROP_CANDIDATES_FOLDER = "candidates/props"  # models/candidates/props/<number>.json: possible new props
# models/candidates/backgrounds/<number>.json: possible new backgrounds, each what a level says of its background
# (see pewpy.tools.background_candidates).
BACKGROUND_CANDIDATES_FOLDER = "candidates/backgrounds"
BACKGROUND_SCROLL_SPEED = 0.2  # a level's usual speed: the candidates scroll at it
LEVEL_FIELDS = ("background", "scenery", "time_of_day", "clouds", "background_seed")  # what a candidate gives a level


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
    """Return the boss candidates, like "candidates/bosses/001", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / BOSS_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    numbers = sorted(entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json"))
    return [f"{BOSS_CANDIDATES_FOLDER}/{number}" for number in numbers if number.isdigit()]


def boss_candidate_parts(name: str) -> list[tuple[str, float, float]]:
    """Return a boss candidate's parts: (drawing, x, y), in cubes from the core's middle (x right, y up the screen)."""
    data, _ = read_model(name)
    return [
        (f"{name}{PART_SEPARATOR}{entry['part']}", float(entry["x"]), float(entry["y"]))
        for entry in data.get("layout", [])
    ]


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


def background_candidate_names() -> list[str]:
    """Return the background candidates, like "007", in order."""
    folder = data_folder() / DRAWINGS_FOLDER / BACKGROUND_CANDIDATES_FOLDER
    if not folder.is_dir():
        return []
    return sorted(entry.name.removesuffix(".json") for entry in folder.iterdir() if entry.name.endswith(".json"))


def background_candidate(name: str) -> tuple[Level, str]:
    """Return a background candidate as a level without waves, and its note (read again every time)."""
    path = data_folder() / DRAWINGS_FOLDER / BACKGROUND_CANDIDATES_FOLDER / f"{name}.json"
    data = json.loads(path.read_text())
    fields = {key: data[key] for key in LEVEL_FIELDS if key in data}
    return Level(name=data.get("name", name), scroll_speed=BACKGROUND_SCROLL_SPEED, waves=(), **fields), data.get(
        "note", ""
    )
