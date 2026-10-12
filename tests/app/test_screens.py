import pytest

from pewpy import config
from pewpy.app import PewPewApp, keys
from pewpy.game.level import parse_level
from pewpy.game.player import SHIPS
from pewpy.game.states import State
from tests.app.driving import choose, complete, frames, labels, menu, play, press, start_level, world


def test_the_main_menu_starts_or_quits(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    assert labels(app) == ["Start", "Dev", "Quit"]
    quit_calls = []
    monkeypatch.setattr(app, "userExit", lambda: quit_calls.append(True))
    menu(app).items[-1] = menu(app).items[-1].__class__("Quit", app.userExit)
    choose(app, "Quit")
    assert quit_calls == [True]


def test_a_level_starts_with_the_ship_flying_in_from_the_bottom(app: PewPewApp) -> None:
    choose(app, "Start")
    choose(app, SHIPS[app.ship_key].name.title())
    choose(app, f"1. {app.worlds[0].name}")
    press(app, keys.MENU_CHOOSE_KEY)
    assert world(app).arriving
    assert world(app).player.y < world(app).view_bottom


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


def test_the_world_select_opens_on_the_world_of_the_last_level_played(app: PewPewApp) -> None:
    app.level_index = app.places.index((2, 1))
    choose(app, "Start")
    choose(app, "Vanguard")
    assert menu(app).selected == 2


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
    assert app.menu_level is not None  # a level's ground behind the menus
    assert app.background.scenery.kind == app.menu_level.scenery_params().name


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


def test_a_bare_ground_draws_its_strips_without_props(app: PewPewApp) -> None:
    play(app)
    app._show_background(parse_level({"background": "savanna", "scenery": {"outposts": None, "flora": None}}))
    terrain = app.background.scenery.terrain
    assert terrain is not None
    assert terrain.props == []
    assert app.background.root.find("**/strip_0")
