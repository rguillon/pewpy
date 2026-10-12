import pytest

from pewpy import app as app_module
from pewpy.app import EFFECTS_RUN_IN, PewPewApp, keys
from pewpy.game.enemies.kinds import BOSSES, drawings
from pewpy.game.states import State
from tests.app.driving import frames, press, start_level, world


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


def test_main_runs_the_game(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = []

    class Game:
        def run(self) -> None:
            ran.append(True)

    monkeypatch.setattr(app_module, "PewPewApp", Game)
    app_module.main()
    assert ran == [True]


def test_the_effects_run_while_the_ai_plays() -> None:
    assert State.AI_PLAYING in EFFECTS_RUN_IN
