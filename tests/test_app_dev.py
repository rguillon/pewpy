"""The Dev menu and its model browser, driven like a player does: keys, menus, frames."""

import json
import shutil
from pathlib import Path

import pytest

from pewpy import data
from pewpy.app import PewPewApp, keys
from pewpy.audio.cues import MENU_MUSIC
from pewpy.dev import music
from pewpy.dev.browser import SIZE_STEP, ModelBrowser
from pewpy.dev.music import MusicBrowser
from pewpy.game.enemies.kinds import MINI_BOSSES
from pewpy.game.states import State
from pewpy.makers.backgrounds.themes import THEMES
from pewpy.ui.menu import Menu
from pewpy.ui.model_browser_view import ROOM, VIEW_SIZE, fit_scale


def menu(app: PewPewApp) -> Menu:
    assert app.menu_view.menu is not None
    return app.menu_view.menu


def press(app: PewPewApp, key: str) -> None:
    app.messenger.send(key)


def choose(app: PewPewApp, label: str) -> None:
    menu(app).selected = [item.label for item in menu(app).items].index(label)
    press(app, keys.MENU_CHOOSE_KEY)


def browser(app: PewPewApp) -> ModelBrowser:
    assert app.model_browser is not None
    return app.model_browser


def texts(app: PewPewApp) -> list[str]:
    view = app.browser_view
    assert view is not None
    return [text.getText() for text in (view.title, view.details, view.info, view.status)]


def test_the_dev_menu_opens_each_category_and_goes_back(app: PewPewApp) -> None:
    choose(app, "Dev")
    assert app.states.state is State.DEV_MENU
    assert [item.label for item in menu(app).items] == [
        "Players",
        "Enemies",
        "Bosses",
        "Music",
        "Backgrounds",
        "AI playing",
        "Screenshots",
        "Back",
    ]
    choose(app, "Enemies")
    assert app.states.state is State.MODEL_BROWSER
    assert app.menu_view.menu is None
    assert browser(app).category == "enemies"
    assert texts(app)[0] == f"Drone  (1/{len(browser(app).models)})"
    assert app.background.root.isHidden()  # a plain dark background
    press(app, keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert app.browser_view is None
    assert menu(app).selected == 1  # back on the category browsed
    assert not app.background.root.isHidden()  # the menus' ground again
    press(app, keys.BACK_KEY)
    assert app.states.state is State.MAIN_MENU


def test_the_keys_browse_reshape_make_and_save_models(app: PewPewApp, data_copy: Path) -> None:
    choose(app, "Dev")
    press(app, "z")  # no model on show: nothing to reshape
    assert app.states.state is State.DEV_MENU
    choose(app, "Players")
    press(app, "arrow_right")
    assert browser(app).entry.key == "juggernaut"
    assert texts(app)[0] == f"Juggernaut  (2/{len(browser(app).models)})"
    assert texts(app)[1] == "Heavy armor, a bit slower"
    width, height = browser(app).size
    press(app, "arrow_up")  # Up and Down: nothing to change
    assert browser(app).size == (width, height)
    press(app, "z")  # taller
    assert browser(app).size == pytest.approx((width, height * SIZE_STEP))
    press(app, "d")  # wider
    assert browser(app).size == pytest.approx((width * SIZE_STEP, height * SIZE_STEP))
    press(app, "s")
    press(app, "q")
    assert browser(app).size == pytest.approx((width, height))
    assert texts(app)[2].startswith(f"Size {width:.3f}")
    press(app, keys.FIRE_KEY)
    assert browser(app).new is not None
    assert texts(app)[3].startswith("New model")
    app.taskMgr.step()  # it sways
    new = browser(app).new
    press(app, keys.MENU_CHOOSE_KEY)
    assert texts(app)[3] == "Saved"
    assert json.loads((data_copy / "models/player/player_heavy.json").read_text()) == new
    assert app.player_models["player_heavy"] is not None  # rebuilt from the new model


def test_a_new_boss_is_saved_and_the_game_reads_it(app: PewPewApp, data_copy: Path) -> None:
    choose(app, "Dev")
    choose(app, "Bosses")
    assert browser(app).entry.key == "sentinel"
    press(app, keys.FIRE_KEY)
    press(app, keys.MENU_CHOOSE_KEY)
    width, height = json.loads((data_copy / "bosses/mini_bosses.json").read_text())["sentinel"]["size"]
    assert (MINI_BOSSES["sentinel"].width, MINI_BOSSES["sentinel"].height) == (width, height)


def test_a_model_that_cant_be_made_says_why(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    choose(app, "Dev")
    choose(app, "Enemies")

    def fail() -> None:
        msg = "no ship that size"
        raise ValueError(msg)

    monkeypatch.setattr(browser(app), "generate", fail)
    press(app, keys.FIRE_KEY)
    assert texts(app)[3] == "no ship that size"


def test_the_bigger_of_the_model_and_its_size_fills_the_view() -> None:
    assert fit_scale(0.5) * 0.5 * ROOM == pytest.approx(VIEW_SIZE)


def music_browser(app: PewPewApp) -> MusicBrowser:
    assert app.music_browser is not None
    return app.music_browser


def music_texts(app: PewPewApp) -> list[str]:
    view = app.music_view
    assert view is not None
    return [text.getText() for text in (view.title, view.details, view.playing, view.status)]


def test_the_music_browser_plays_makes_and_saves_songs(
    app: PewPewApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shutil.copytree(data.SOURCE_DATA / "music", tmp_path / "music")
    monkeypatch.setattr(music, "data_folder", lambda: tmp_path)
    choose(app, "Dev")
    choose(app, "Music")
    assert app.states.state is State.MUSIC_BROWSER
    assert app.menu_view.menu is None
    assert music_texts(app)[0] == "title  (1/12)"
    app.taskMgr.step()
    assert app.audio.wanted == music_browser(app).music()
    assert music_texts(app)[2] == "Rendering..."  # the tests render no songs
    press(app, "arrow_right")
    press(app, "arrow_up")  # nothing to change
    assert music_texts(app)[0] == "world_1  (2/12)"
    press(app, keys.FIRE_KEY)
    browser = music_browser(app)
    assert browser.new is not None
    assert app.audio.library.has(browser.name())
    assert music_texts(app)[3].startswith("New song")
    app.taskMgr.step()
    assert app.audio.wanted == browser.music()
    app.audio.playing = browser.music()
    app.taskMgr.step()
    assert music_texts(app)[2] == "Playing"
    press(app, keys.MUSIC_KEY)
    app.taskMgr.step()
    assert music_texts(app)[2] == "Music off: M turns it on"
    press(app, keys.MUSIC_KEY)
    press(app, keys.MENU_CHOOSE_KEY)
    assert music_texts(app)[3] == "Saved"
    assert (tmp_path / "music" / "world_1.mid").read_bytes() == browser.new
    press(app, keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert app.music_view is None
    assert menu(app).selected == 3  # back on Music
    app.taskMgr.step()
    assert app.audio.wanted == MENU_MUSIC


def test_the_screenshots_take_and_save_a_moment_of_each_world(
    app: PewPewApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pewpy.dev import screenshots  # noqa: PLC0415 - the module whose folder is changed

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


def test_the_backgrounds_show_a_candidate_of_each_theme(app: PewPewApp) -> None:
    choose(app, "Dev")
    choose(app, "Backgrounds")
    assert app.states.state is State.BACKGROUND_BROWSER
    assert app.menu_view.menu is None
    browser, view = app.background_browser, app.background_view
    assert browser is not None
    assert view is not None
    assert app.menu_level == browser.level()  # its ground scrolls by
    assert view.title.getText() == browser.title()
    assert view.status.getText() == f"theme: {browser.theme}"
    seed = browser.seed
    press(app, keys.FIRE_KEY)  # another one of the theme
    assert browser.index == 0
    assert browser.seed != seed
    assert view.details.getText() == browser.details()
    press(app, "arrow_left")  # the last theme
    assert browser.index == len(THEMES) - 1
    assert app.menu_level == browser.level()
    press(app, "arrow_up")  # nothing to change
    assert browser.index == len(THEMES) - 1
    press(app, keys.MENU_CHOOSE_KEY)  # nothing to save
    assert app.states.state is State.BACKGROUND_BROWSER
    press(app, keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert app.background_view is None
    assert app.background_browser is None
    assert menu(app).items[menu(app).selected].label == "Backgrounds"
