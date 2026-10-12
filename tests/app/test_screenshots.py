from pathlib import Path

import pytest

from pewpy.app import PewPewApp, keys
from pewpy.game.states import State
from tests.app.driving import choose, menu, press


def test_the_screenshots_take_and_save_a_moment_of_each_world(
    app: PewPewApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pewpy.generators import screenshots  # noqa: PLC0415 - the module whose folder is changed

    monkeypatch.setattr(screenshots, "SCREENSHOTS", tmp_path)
    monkeypatch.setattr(screenshots, "TIMES", (0.5, 0.5))  # short shots
    monkeypatch.setattr(screenshots, "BOSS_SHARE", 0.0)
    app.level_index = 0  # it opens on the world of the last level played
    choose(app, "Dev")
    choose(app, "Screenshots")
    assert app.states.state is State.SCREENSHOTS
    view = app.screenshot_view
    assert view is not None
    assert view.title.getText() == f"World 1: {app.worlds[0].name}  (1/{len(app.worlds)})"
    press(app, keys.MENU_CHOOSE_KEY)  # nothing to save yet
    assert not list(tmp_path.iterdir())
    assert app.menu_level is app.worlds[0].levels[0]  # the world's ground until a shot is taken
    press(app, "arrow_left")  # the last world
    press(app, "arrow_up")  # nothing to change
    assert app.shot_world == len(app.worlds) - 1
    assert app.menu_level is app.worlds[-1].levels[0]
    press(app, keys.FIRE_KEY)
    assert app.world is not None
    assert app.world.level in app.worlds[-1].levels  # one of its levels
    assert view.details.getText().startswith(f"{len(app.worlds)}-")
    assert app.menu_level is None  # the shot's level, not the menus' ground
    assert view.status.getText() == "Enter saves it as the world's screenshot"
    press(app, keys.MENU_CHOOSE_KEY)
    assert (tmp_path / f"world_{len(app.worlds)}.png").is_file()
    assert view.status.getText() == f"Saved to {tmp_path.name}/world_{len(app.worlds)}.png"
    assert not view.root.isHidden()
    press(app, "arrow_right")  # another world: the shot is dropped
    assert app.shot_world == 0
    assert app.world is None
    assert app.menu_level is app.worlds[0].levels[0]
    press(app, keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert app.screenshot_view is None
    assert menu(app).items[menu(app).selected].label == "Screenshots"
