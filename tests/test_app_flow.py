"""The game app's screens and game flow, driven like a player does: keys, menus, frames."""

import pytest

from pewpy import app as app_module
from pewpy import config
from pewpy.app import PewPewApp, keys, window
from pewpy.game.enemies.kinds import BOSSES, drawings
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from pewpy.game.world import World
from pewpy.ui.menu import Menu


def frames(app: PewPewApp, count: int = 1) -> None:
    for _ in range(count):
        app.taskMgr.step()


def menu(app: PewPewApp) -> Menu:
    assert app.menu_view.menu is not None
    return app.menu_view.menu


def world(app: PewPewApp) -> World:
    assert app.world is not None
    return app.world


def labels(app: PewPewApp) -> list[str]:
    return [item.label for item in menu(app).items]


def press(app: PewPewApp, key: str) -> None:
    app.messenger.send(key)


def choose(app: PewPewApp, label: str) -> None:
    menu(app).selected = labels(app).index(label)
    press(app, keys.MENU_CHOOSE_KEY)


def start_level(app: PewPewApp, index: int = 0) -> None:
    choose(app, "Start")
    choose(app, SHIPS[app.ship_key].name.title())
    world_index, number = app.places[index]
    choose(app, f"{world_index + 1}. {app.worlds[world_index].name}")
    menu(app).selected = number - 1
    press(app, keys.MENU_CHOOSE_KEY)
    world(app).arrival_time = 0.0  # skip the ship flying in


def test_a_level_starts_with_the_ship_flying_in_from_the_bottom(app: PewPewApp) -> None:
    choose(app, "Start")
    choose(app, SHIPS[app.ship_key].name.title())
    choose(app, f"1. {app.worlds[0].name}")
    press(app, keys.MENU_CHOOSE_KEY)
    assert world(app).arriving
    assert world(app).player.y < world(app).view_bottom


def test_the_main_menu_starts_or_quits(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    assert labels(app) == ["Start", "Quit"]
    quit_calls = []
    monkeypatch.setattr(app, "userExit", lambda: quit_calls.append(True))
    menu(app).items[-1] = menu(app).items[-1].__class__("Quit", app.userExit)
    choose(app, "Quit")
    assert quit_calls == [True]


def test_the_arrows_move_the_highlight_and_escape_goes_back(app: PewPewApp) -> None:
    choose(app, "Start")
    assert app.states.state is State.SHIP_SELECT
    assert app.ship_select is not None
    first = menu(app).selected
    press(app, "arrow_down")
    assert menu(app).selected == (first + 1) % len(labels(app))
    assert "arrow_down" in app.keys_down
    press(app, "arrow_down-up")
    assert "arrow_down" not in app.keys_down
    frames(app)
    press(app, keys.BACK_KEY)
    assert app.states.state is State.MAIN_MENU
    assert app.ship_select is None


def test_a_ship_then_a_world_then_a_level(app: PewPewApp) -> None:
    choose(app, "Start")
    choose(app, "Phantom")
    assert app.ship_key == "phantom"
    assert app.states.state is State.WORLD_SELECT
    assert labels(app)[-1] == "Back"
    choose(app, "Back")
    assert app.states.state is State.SHIP_SELECT
    choose(app, "Phantom")
    choose(app, f"2. {app.worlds[1].name}")
    assert app.states.state is State.LEVEL_SELECT
    assert labels(app)[0].startswith("2-1 ")
    assert menu(app).selected == 0  # the last level played is in another world
    press(app, "arrow_up")  # onto "Back": no level to preview
    frames(app)
    press(app, "arrow_down")  # the first level again
    frames(app, 2)
    press(app, "arrow_down")  # the next one: the preview changes level
    assert app.level_preview.shown == app.places.index((1, 2))
    frames(app)
    choose(app, "Back")
    assert app.states.state is State.WORLD_SELECT


def test_playing_a_level(app: PewPewApp) -> None:
    start_level(app, 1)
    assert app.states.state is State.PLAYING
    assert app.menu_view.menu is None
    assert app.world is not None
    assert world(app).level is app.levels[1]
    assert app.background.scenery.kind != "space"
    bosses = [wave.enemy for wave in world(app).level.waves if wave.enemy in BOSSES]
    assert bosses
    assert all(drawing in app.ship_models for wave in world(app).level.waves for drawing in drawings(wave.enemy))
    press(app, keys.FIRE_KEY)
    press(app, "arrow_left")
    frames(app, 5)
    assert world(app).player.x < 0
    assert world(app).player_bullets or world(app).time > 0
    selected = world(app).arsenal.selected
    press(app, keys.SWITCH_WEAPON_KEY)
    assert world(app).arsenal.selected != selected


def test_pausing_and_going_on(app: PewPewApp) -> None:
    start_level(app)
    press(app, keys.BACK_KEY)
    assert app.states.state is State.PAUSED
    assert labels(app) == ["Resume", "Main menu"]
    press(app, keys.BACK_KEY)  # the pause menu's back: play on
    assert app.states.state is State.PLAYING
    press(app, keys.BACK_KEY)
    choose(app, "Main menu")
    assert app.states.state is State.MAIN_MENU
    assert app.world is None
    assert app.background.scenery.kind == "space"


def test_the_weapon_only_switches_while_playing(app: PewPewApp) -> None:
    press(app, keys.SWITCH_WEAPON_KEY)  # on the main menu: nothing to switch
    assert app.world is None


def test_game_over_and_continue(app: PewPewApp) -> None:
    start_level(app, 2)
    world(app).player.health = 0
    world(app).lives = 1
    frames(app)
    assert app.states.state is State.GAME_OVER
    assert labels(app) == ["Continue", "Main menu"]
    world(app).score = 500
    choose(app, "Continue")
    assert app.states.state is State.PLAYING
    assert app.level_index == 2
    assert world(app).score == 0
    assert world(app).lives == config.PLAYER_LIVES


def complete(app: PewPewApp) -> None:
    world(app).pending_spawns = []
    world(app).enemies = []
    frames(app)
    assert app.states.state is State.PLAYING  # the ship flies away first
    world(app).player.y = world(app).view_top + 1.0
    frames(app)


def test_a_level_complete_goes_on_to_the_next_level_keeping_the_score(app: PewPewApp) -> None:
    start_level(app, 0)
    complete(app)
    assert app.states.state is State.LEVEL_COMPLETE
    assert menu(app).title == "LEVEL COMPLETE"
    world(app).score = 1234
    choose(app, "Next level")
    assert app.states.state is State.PLAYING
    assert app.level_index == 1
    assert world(app).score == 1234


def test_the_last_level_of_a_world_goes_on_to_the_next_world(app: PewPewApp) -> None:
    last = len(app.worlds[0].levels) - 1
    start_level(app, last)
    complete(app)
    assert menu(app).title.startswith("WORLD COMPLETE")
    choose(app, "Next world")
    assert app.places[app.level_index] == (1, 1)


def test_the_last_level_wins_the_game(app: PewPewApp) -> None:
    start_level(app, len(app.levels) - 1)
    complete(app)
    assert menu(app).title.endswith("YOU WIN!")
    assert labels(app) == ["Main menu"]
    app._next_level()  # nothing after the last level: back to the main menu
    assert app.states.state is State.MAIN_MENU


def test_the_world_select_opens_on_the_world_of_the_last_level_played(app: PewPewApp) -> None:
    app.level_index = app.places.index((2, 1))
    choose(app, "Start")
    choose(app, "Vanguard")
    assert menu(app).selected == 2


def test_the_music_key_turns_the_music_off_and_on(app: PewPewApp) -> None:
    on = app.audio.music_on
    press(app, keys.MUSIC_KEY)
    assert app.audio.music_on is not on
    press(app, keys.MUSIC_KEY)
    assert app.audio.music_on is on


@pytest.mark.parametrize("driver", ["d3d12", ""])
def test_leaving_the_game(app: PewPewApp, monkeypatch: pytest.MonkeyPatch, driver: str) -> None:
    exits, finals = [], []
    monkeypatch.setenv("GALLIUM_DRIVER", driver)
    monkeypatch.setattr(window.os, "_exit", exits.append)
    monkeypatch.setattr(window.ShowBase, "finalizeExit", lambda _self: finals.append(True))
    app.finalizeExit()
    assert (exits, finals) == (([0], [True]) if driver else ([], [True]))


def test_main_runs_the_game(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = []

    class Game:
        def run(self) -> None:
            ran.append(True)

    monkeypatch.setattr(app_module, "PewPewApp", Game)
    app_module.main()
    assert ran == [True]


def test_a_menu_view_without_a_menu_has_nothing_to_highlight(app: PewPewApp) -> None:
    app.menu_view.show(None)
    app.menu_view.refresh()
    assert app.menu_view.texts == []
