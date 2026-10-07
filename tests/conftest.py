"""The game app for the tests that need one (the `app` fixture), and a copy of the data to change (`data_copy`).

One for the whole session (Panda3D allows a single ShowBase), drawing into an offscreen buffer through EGL, so no
display is needed, and silent.
"""

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from panda3d.core import loadPrcFileData

from pewpy import data
from pewpy.app import PewPewApp
from pewpy.audio.library import Library
from pewpy.game.enemies import spec
from pewpy.game.enemies.kinds import reload_kinds
from pewpy.game.states import State
from pewpy.generators.models import catalog, saving


@pytest.fixture(scope="session")
def game_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator:
    loadPrcFileData("", "window-type offscreen\nload-display p3headlessgl\naudio-library-name null\nsync-video false")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.mktemp("cache")))
        patch.setattr(Library, "request", lambda *_, **__: None)  # no songs rendered
        app = PewPewApp()
        yield app
    app.destroy()


@pytest.fixture
def app(game_app: PewPewApp) -> PewPewApp:
    """Return the game app, back on the main menu."""
    game_app.keys_down.clear()
    game_app.world = None
    previous, game_app.states.state = game_app.states.state, State.MAIN_MENU
    game_app._on_state_change(previous, State.MAIN_MENU)
    return game_app


@pytest.fixture
def data_copy(tmp_path: Path, request: pytest.FixtureRequest) -> Iterator[Path]:
    """Give the game a copy of its ships', enemies' and bosses' data and models, to change (the Dev menu's browser).

    Afterwards, the game reads its own again (and the app, if the test has it, builds its models from them).
    """
    root = tmp_path / "data"
    source = data.SOURCE_DATA
    for name in ("enemies", "bosses", *(f"models/{group}" for group in data.MODEL_GROUPS)):
        shutil.copytree(source / name, root / name)
    shutil.copy(source / "ships.json", root / "ships.json")
    app = request.getfixturevalue("game_app") if "app" in request.fixturenames else None
    with pytest.MonkeyPatch.context() as patch:
        for module in (data, catalog, saving, spec):
            patch.setattr(module, "data_folder", lambda: root)
        yield root
    reload_kinds()
    if app is not None:
        app._build_models()
