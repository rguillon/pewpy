"""The game app for the tests that need one (the `app` fixture): one for the whole session (Panda3D allows a single
ShowBase), drawing into an offscreen buffer through EGL, so no display is needed, and silent.
"""

from collections.abc import Iterator

import pytest
from panda3d.core import loadPrcFileData

from pewpy.audio.library import Library


@pytest.fixture(scope="session")
def game_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator:
    loadPrcFileData("", "window-type offscreen\nload-display p3headlessgl\naudio-library-name null\nsync-video false")
    from pewpy.app import PewPewApp

    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.mktemp("cache")))
        patch.setattr(Library, "request", lambda self, name, loop=True, first=True: None)  # no songs rendered
        app = PewPewApp()
        yield app
    app.destroy()


@pytest.fixture
def app(game_app):
    """The game app, back on the main menu."""
    from pewpy.game.states import State

    game_app.keys_down.clear()
    game_app.world = None
    previous, game_app.states.state = game_app.states.state, State.MAIN_MENU
    game_app._on_state_change(previous, State.MAIN_MENU)
    return game_app
