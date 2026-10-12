import pytest

from pewpy import config
from pewpy.app import PewPewApp
from pewpy.game.enemies.kinds import BOSSES
from pewpy.game.enemies.roster import make_enemy
from pewpy.game.weapons.player.secondary import SecondaryWeapon
from tests.app.driving import node, play


def test_a_boss_and_its_parts_are_drawn_and_its_health_bar_shows_once_on_screen(app: PewPewApp) -> None:
    world = play(app)
    boss = make_enemy("rockbreaker", 0.0, 0.0, "left", None, world.view_top)
    boss.y = world.view_top + boss.height  # still above the screen
    world.enemies = [boss, *boss.parts]
    app._update_hud()
    assert app.boss_hud.isHidden()
    boss.y = 0.3
    app._update_hud()
    assert not app.boss_hud.isHidden()
    assert app.boss_name.getText() == BOSSES["rockbreaker"].name
    app._update_hud()  # the same boss: nothing to change
    assert node(app, boss) is not None
    assert node(app, boss.parts[0]) is not None
    world.enemies = []
    app._update_hud()
    assert app.boss_hud.isHidden()


def test_the_hud_shows_the_secondary_weapon(app: PewPewApp) -> None:
    world = play(app)
    world.arsenal.secondary = SecondaryWeapon("lightning")
    app._update_hud()
    assert app.secondary_text.getText() == "Z"
    assert not app.secondary_tile.isHidden()
    world.arsenal.secondary = None
    app._update_hud()
    assert app.secondary_text.getText() == ""
    assert app.secondary_tile.isHidden()


def test_the_frames_per_second_can_be_hidden(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "SHOW_FPS", False)
    app._setup_hud()
    assert app.fps_text.getParent().isHidden()
    app._update_fps()  # not counted while hidden
    monkeypatch.setattr(config, "SHOW_FPS", True)
    app._setup_hud()
    app._fps_next = 0.0
    app._update_fps()
    assert app.fps_text.getText().endswith("FPS")
