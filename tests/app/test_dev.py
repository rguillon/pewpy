import json
import shutil
from pathlib import Path

import pytest

from pewpy import data
from pewpy.app import PewPewApp, keys
from pewpy.audio.cues import MENU_MUSIC
from pewpy.game.enemies.kinds import MINI_BOSSES
from pewpy.game.states import State
from pewpy.generators.models.browser import SIZE_STEP, ModelBrowser
from pewpy.generators.models.parts import KINDS
from pewpy.generators.music import browser as music
from pewpy.generators.music.browser import MusicBrowser
from tests.app.driving import choose, menu, press


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
        "Parts",
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
    assert new is not None
    assert json.loads((data_copy / "models/player/player_heavy.json").read_text()) == new["core"]
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


def test_the_parts_menu_opens_the_parts_browser_on_each_kind(app: PewPewApp) -> None:
    choose(app, "Dev")
    choose(app, "Parts")
    assert app.states.state is State.PARTS_MENU
    assert menu(app).title == "PARTS"
    assert [item.label for item in menu(app).items] == [*KINDS.values(), "Back"]
    choose(app, "Wings")
    assert app.states.state is State.MODEL_BROWSER
    parts = app.part_browser
    assert parts is not None
    assert app.model_browser is None
    assert texts(app)[0] == f"Swept wing, tiny  (1/{len(parts.parts)})"
    assert texts(app)[1].startswith("Wings. ")
    press(app, "arrow_left")  # wrapping around, within the kind
    assert (parts.kind, parts.index) == ("wing", len(parts.parts) - 1)
    press(app, "arrow_right")
    press(app, "arrow_right")
    press(app, "arrow_down")  # nothing to change
    assert (parts.kind, parts.index) == ("wing", 1)
    app.taskMgr.step()  # it sways
    press(app, keys.FIRE_KEY)  # nothing to make
    press(app, keys.MENU_CHOOSE_KEY)  # nor to save
    assert app.states.state is State.MODEL_BROWSER
    press(app, keys.BACK_KEY)
    assert app.states.state is State.PARTS_MENU
    assert app.browser_view is None
    assert app.part_browser is None
    assert menu(app).selected == 1  # back on Wings
    press(app, keys.BACK_KEY)
    assert app.states.state is State.DEV_MENU
    assert menu(app).selected == 3  # back on Parts


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
    assert menu(app).selected == 4  # back on Music
    app.taskMgr.step()
    assert app.audio.wanted == MENU_MUSIC
