"""The AI playing screen, driven like a player does: keys, menus, frames."""

from pathlib import Path

import numpy as np
import pytest

from pewpy.ai import files
from pewpy.ai.brain import Brain
from pewpy.app import EFFECTS_RUN_IN, PewPewApp, keys
from pewpy.audio.cues import music
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.game.world import World
from pewpy.ui.ai_panel import playing_text
from pewpy.ui.menu import Menu


@pytest.fixture(autouse=True)
def ai_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """No brain saved, unless a test saves one."""
    monkeypatch.setattr(files, "brain_folder", lambda: tmp_path)
    return tmp_path


def menu(app: PewPewApp) -> Menu:
    assert app.menu_view.menu is not None
    return app.menu_view.menu


def world(app: PewPewApp) -> World:
    assert app.world is not None
    return app.world


def choose(app: PewPewApp, label: str) -> None:
    menu(app).selected = [item.label for item in menu(app).items].index(label)
    app.messenger.send(keys.MENU_CHOOSE_KEY)


def watch(app: PewPewApp, index: int = 0, ship: str = "juggernaut") -> None:
    """Pick a ship and a level for the AI with the menus, from the Dev menu."""
    choose(app, "Dev")
    choose(app, "AI playing")
    assert menu(app).title == "AI PLAYING\nSELECT SHIP"
    choose(app, SHIPS[ship].name.title())
    world_index, number = app.places[index]
    choose(app, f"{world_index + 1}. {app.worlds[world_index].name}")
    assert menu(app).title.startswith("AI PLAYING\n")
    menu(app).selected = number - 1
    app.messenger.send(keys.MENU_CHOOSE_KEY)


def panel(app: PewPewApp) -> str:
    return app.ai_panel.text.getText()


def clear_level(app: PewPewApp) -> None:
    world(app).pending_spawns = []
    world(app).enemies = []
    app.taskMgr.step()


def test_the_ai_plays_the_level_picked_with_the_ship_picked(app: PewPewApp) -> None:
    watch(app, 2)
    assert app.states.state is State.AI_PLAYING
    assert app.menu_view.menu is None
    assert world(app).level is app.levels[2]
    assert world(app).ship is SHIPS["juggernaut"]
    app.taskMgr.step()
    app.taskMgr.step()
    assert world(app).time > 0
    assert not app.ai_panel.text.isHidden()
    assert panel(app).startswith("AI PLAYING  no brain yet: a new one plays")
    assert f"On screen: {SHIPS['juggernaut'].name} on 1-3 {app.levels[2].name}" in panel(app)


def test_the_ai_goes_on_to_the_next_level_then_a_new_game_at_game_over(app: PewPewApp) -> None:
    watch(app, 0)
    world(app).score = 900
    clear_level(app)
    assert app.level_index == 1
    assert world(app).score == 900
    world(app).player.health = 0
    world(app).lives = 1
    app.taskMgr.step()
    assert app.level_index == 0  # a new game from the level picked
    assert world(app).score == 0
    assert app.ai_game.games == 2
    assert (app.ai_game.cleared, app.ai_game.best) == (1, 1)
    assert "Games from 1-1: 1, 1-1 cleared in 1 (100%)" in panel(app)


def test_after_the_last_level_a_new_game_starts(app: PewPewApp) -> None:
    last = len(app.levels) - 1
    watch(app, last)
    clear_level(app)
    assert app.level_index == last
    assert app.ai_game.games == 2


def test_the_saved_brain_plays(app: PewPewApp, ai_folder: Path) -> None:
    files.save_training(ai_folder, files.Training(Brain.random(np.random.default_rng(1)), generation=40))
    watch(app)
    assert app.ai_game.generation == 40
    app.taskMgr.step()
    assert panel(app).startswith("AI PLAYING  the brain at generation 40")


def test_escape_goes_back_to_the_level_select_then_the_menus_pick_for_the_player_again(app: PewPewApp) -> None:
    watch(app, 1)
    app.taskMgr.step()
    app.messenger.send(keys.BACK_KEY)
    assert app.states.state is State.LEVEL_SELECT
    assert app.world is None
    assert app.ai_panel.text.isHidden()
    assert menu(app).selected == 1  # on the level the AI played
    assert menu(app).title.startswith("AI PLAYING\n")
    choose(app, "Back")
    choose(app, "Back")
    choose(app, "Back")  # the ship select goes back to the Dev menu, on AI playing
    assert app.states.state is State.DEV_MENU
    assert menu(app).items[menu(app).selected].label == "AI playing"
    choose(app, "Back")
    choose(app, "Start")
    assert menu(app).title == "SELECT SHIP"
    choose(app, "Back")  # the player's ship select goes back to the main menu
    assert app.states.state is State.MAIN_MENU


def test_the_ai_plays_to_the_worlds_music_with_the_effects_running() -> None:
    assert State.AI_PLAYING in EFFECTS_RUN_IN
    assert music(State.AI_PLAYING, 2, boss=False).song == "world_3"


def test_the_text_tells_how_the_games_went() -> None:
    assert "Games" not in playing_text(None, "here", "1-1", games=1, cleared=0, best=0)
    text = playing_text(3, "here", "2-1", games=5, cleared=1, best=2)
    assert "Games from 2-1: 4, 2-1 cleared in 1 (25%)" in text
    assert "Best game: 2 levels cleared" in text
