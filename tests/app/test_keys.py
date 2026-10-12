import pytest
from panda3d.core import ButtonThrower, KeyboardButton, ModifierButtons, MouseWatcher, NodePath

from pewpy.app import PewPewApp, keys
from pewpy.game.states import State
from tests.app.driving import choose, frames, labels, menu, play, press


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


def test_the_weapon_only_switches_while_playing(app: PewPewApp) -> None:
    press(app, keys.SWITCH_WEAPON_KEY)  # on the main menu: nothing to switch
    assert app.world is None


def test_enter_does_nothing_while_playing_and_escape_nothing_without_a_menu(app: PewPewApp) -> None:
    play(app)
    app.messenger.send(keys.MENU_CHOOSE_KEY)
    assert app.states.state is State.PLAYING
    app.states.transition(State.PAUSED)
    app.menu_view.menu = None  # (no screen of the game is like that: the dev tools' are)
    app.messenger.send(keys.BACK_KEY)
    assert app.states.state is State.PAUSED


def test_shift_never_turns_space_into_shift_space(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    watcher = NodePath(MouseWatcher("watcher"))
    thrower = ButtonThrower("thrower")
    shift = ModifierButtons()
    shift.addButton(KeyboardButton.shift())
    thrower.setModifierButtons(shift)
    watcher.attachNewNode(thrower)
    monkeypatch.setattr(app, "mouseWatcher", watcher)
    monkeypatch.setattr(app, "mouseWatcherNode", watcher.node())
    app._disable_modifier_keys()
    assert thrower.getModifierButtons().getNumButtons() == 0
