"""The game app drawing a level being played: every kind of thing on screen, the effects, the HUD."""

import math

import pytest
from panda3d.core import ButtonThrower, KeyboardButton, ModifierButtons, MouseWatcher, NodePath

from pewpy import app as app_module
from pewpy import config
from pewpy.app import PewPewApp
from pewpy.game.enemies.enemy import Enemy, make
from pewpy.game.enemies.kinds import BOSSES, ENEMIES
from pewpy.game.enemies.roster import make_enemy
from pewpy.game.entities import Bullet, Pickup
from pewpy.game.states import State
from pewpy.game.weapons.bullets import Missile
from pewpy.game.weapons.player.arsenal import Beam
from pewpy.game.weapons.player.secondary import SecondaryWeapon
from pewpy.game.world import Event, World
from pewpy.graphics import models


def play(app: PewPewApp, index: int = 0) -> World:
    app.states.transition(State.SHIP_SELECT)
    app.states.transition(State.WORLD_SELECT)
    app.states.transition(State.LEVEL_SELECT)
    app._start_level(index)
    assert app.world is not None
    app.world.pending_spawns = []  # only what the test puts in
    return app.world


def node(app: PewPewApp, entity) -> NodePath:
    app._sync_nodes()
    return app.nodes[entity]


def test_every_kind_of_ship_gets_its_model(app):
    world = play(app)
    world.enemies = [make(kind, 0.0, 0.5) for kind in ENEMIES]
    app._sync_nodes()
    assert all(enemy in app.nodes for enemy in world.enemies)
    world.enemies = []
    app._sync_nodes()  # gone from the world: gone from the screen
    assert set(app.nodes) == {world.player}


def test_a_boss_and_its_parts_are_drawn_and_its_health_bar_shows_once_on_screen(app):
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
    assert node(app, boss) is not None and node(app, boss.parts[0]) is not None
    world.enemies = []
    app._update_hud()
    assert app.boss_hud.isHidden()


@pytest.mark.parametrize(
    ("appearance", "hidden", "shade"),
    [("hidden", True, None), ("flash", False, None), ("hit", False, app_module.HIT_SHADE), ("normal", False, None)],
)
def test_enemies_show_how_they_are_doing(app, monkeypatch, appearance, hidden, shade):
    world = play(app)
    drone = make("drone", 0.0, 0.5)
    world.enemies = [drone]
    monkeypatch.setattr(drone, "appearance", lambda: appearance)
    shown = node(app, drone)
    assert shown.isHidden() is hidden
    if shade:
        assert tuple(shown.getColorScale()) == pytest.approx(shade, abs=1e-3)
    if appearance == "flash":
        assert tuple(shown.getColor()) == pytest.approx(app_module.FLASH_COLOR)


def test_a_shield_carrier_shows_its_bubble_only_while_shielded(app, monkeypatch):
    world = play(app)
    carrier = make("shield_carrier", 0.0, 0.5)
    world.enemies = [carrier]
    monkeypatch.setattr(carrier, "appearance", lambda: "shield")
    assert not node(app, carrier).find("**/shield").isHidden()
    monkeypatch.setattr(carrier, "appearance", lambda: "armored")
    shown = node(app, carrier)
    assert shown.find("**/shield").isHidden()
    assert tuple(shown.getColorScale()) == pytest.approx(app_module.ARMORED_SHADE, abs=1e-3)


def moving(enemy: Enemy, vx: float, vy: float) -> Enemy:
    enemy.vx, enemy.vy = vx, vy
    return enemy


def test_enemies_turn_to_aim_or_fly(app):
    world = play(app)
    world.player.x, world.player.y = 0.0, -0.5
    turret = make("turret", 0.5, 0.0)
    diver = moving(make("diver", 0.0, 0.5), 0.3, -0.3)
    diver.go_to("dive")
    swarmer = moving(make("swarmer", 0.0, 0.5), 0.4, 0.0)
    mine = make("mine", 0.0, 0.5)
    mine.age = 1.0
    world.enemies = [turret, diver, swarmer, mine]
    barrel = node(app, turret).find("**/barrel")
    assert barrel.getR() == pytest.approx(models.facing_roll(-0.5, -0.5))
    assert node(app, diver).getR() == pytest.approx(models.facing_roll(0.3, -0.3))
    assert node(app, swarmer).getR() == pytest.approx(models.facing_roll(0.4, 0.0))
    assert node(app, mine).getR() == pytest.approx(app_module.MINE_SPIN_SPEED)


def test_missiles_point_where_they_fly_and_pickups_spin(app):
    world = play(app)
    missile = Missile(x=0.0, y=0.0, vx=0.5, vy=0.5)
    pickup = Pickup(x=0.2, y=0.2, kind="laser")
    world.player_bullets = [missile]
    world.pickups = [pickup]
    world.time = 1.0
    assert node(app, missile).getR() == pytest.approx(models.facing_roll(0.5, 0.5))
    assert node(app, pickup).getH() == pytest.approx(app_module.PICKUP_SPIN_SPEED)


def test_the_player_banks_blinks_and_carries_its_secondary_weapon(app):
    world = play(app)
    player = world.player
    player.vx = player.ship.speed
    player.invulnerable_time = 0.15  # blinking: hidden this tenth of a second
    shown = node(app, player)
    assert shown.isHidden()
    assert shown.getH() == pytest.approx(-app_module.PLAYER_BANK_ANGLE)
    assert shown.find("secondary_turret").isHidden()
    world.arsenal.secondary = SecondaryWeapon("turret", aim_x=1.0, aim_y=0.0)
    player.invulnerable_time = 0.0
    shown = node(app, player)
    assert not shown.isHidden()
    assert not shown.find("secondary_turret").isHidden()
    assert shown.find("secondary_turret/**/barrel").getR() == pytest.approx(models.facing_roll(1.0, 0.0))
    world.arsenal.secondary = SecondaryWeapon("lightning")
    shown = node(app, player)
    assert shown.find("secondary_turret").isHidden() and not shown.find("secondary_lightning").isHidden()


def test_bullets_are_sprites_colored_by_who_fired_them(app):
    player_shot = Bullet(x=0.0, y=0.0, width=0.02, height=0.05)
    sniper = Bullet(x=0.0, y=0.0, hostile=True, style="sniper")
    pellet = Bullet(x=0.0, y=0.0, hostile=True, style="pellet")
    beam = Bullet(x=0.0, y=0.0, width=0.04, height=1.0, hostile=True, style="beam")
    assert app_module._bullet_sprite(player_shot).color == app_module.PLAYER_BULLET_COLOR
    assert app_module._bullet_sprite(sniper).color == app_module.SNIPER_BULLET_COLOR
    assert app_module._bullet_sprite(pellet).color == app_module.ENEMY_BULLET_COLOR
    assert app_module._bullet_sprite(beam).height == 1.0  # as long as the beam: only its sides glow
    world = play(app)
    world.enemy_bullets = [sniper, beam]
    app._sync_nodes()
    assert sniper not in app.nodes  # drawn as sprites, not models


def test_the_laser_beam_shows_while_firing(app):
    world = play(app)
    world.laser = Beam(x=0.1, bottom=-0.5, top=0.9, width=0.05)
    world.events = [Event("burn", 0.1, 0.4)]
    glow = app._laser_glow(world)
    assert glow is not None and glow.hits == (0.4,)
    app._sync_nodes()
    assert not app.laser_node.isHidden()
    assert app.laser_node.getX() == pytest.approx(0.1)
    world.laser = None
    assert app._laser_glow(world) is None
    app._sync_nodes()
    assert app.laser_node.isHidden()


def test_the_lightning_bolt_zigzags_to_what_it_struck(app):
    world = play(app)
    world.bolt = [(0.0, -0.5), (0.0, -0.5), (0.3, 0.2)]  # a zero-length step too
    app._sync_nodes()
    assert app.bolt_node.getNumChildren() == 1
    world.bolt = []
    app._sync_nodes()
    assert app.bolt_node.getNumChildren() == 0


def test_every_event_plays_its_effect(app, monkeypatch):
    play(app)
    played = []
    monkeypatch.setattr(app.effects, "play", played.append)
    events = [
        Event("impact", 0.0, 0.0, source="enemy"),
        Event("impact", 0.0, 0.0, source="player"),
        Event("explosion", 0.0, 0.0, 0.1, "drone"),
        Event("explosion", 0.0, 0.0, 0.1, "unknown"),
        Event("blast", 0.0, 0.0, 0.1),
        Event("burn", 0.0, 0.0),
        Event("disarmed", 0.0, 0.0, source="turret"),
        Event("hurt", 0.0, 0.0),  # sound only
    ]
    app._show_events(events, 1 / 60)
    assert len(played) == 7


def test_the_hud_shows_the_secondary_weapon(app):
    world = play(app)
    world.arsenal.secondary = SecondaryWeapon("lightning")
    app._update_hud()
    assert app.secondary_text.getText() == "+Z"
    world.arsenal.secondary = None
    app._update_hud()
    assert app.secondary_text.getText() == ""


def test_the_frames_per_second_can_be_hidden(app, monkeypatch):
    monkeypatch.setattr(config, "SHOW_FPS", False)
    app._setup_hud()
    assert app.fps_text.getParent().isHidden()
    app._update_fps()  # not counted while hidden
    monkeypatch.setattr(config, "SHOW_FPS", True)
    app._setup_hud()
    app._fps_next = 0.0
    app._update_fps()
    assert app.fps_text.getText().endswith("FPS")


def test_enter_does_nothing_while_playing_and_escape_nothing_without_a_menu(app):
    play(app)
    app.messenger.send(app_module.MENU_CHOOSE_KEY)
    assert app.states.state is State.PLAYING
    app.states.transition(State.PAUSED)
    app.menu_view.menu = None  # (no screen of the game is like that: the dev tools' are)
    app.messenger.send(app_module.BACK_KEY)
    assert app.states.state is State.PAUSED


def test_shift_never_turns_space_into_shift_space(app, monkeypatch):
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


def test_the_letterbox_follows_the_window(app, monkeypatch):
    class Sizeless:
        def hasSize(self) -> bool:
            return False

    monkeypatch.setattr(app, "win", Sizeless())
    app._fit_letterbox()  # the window isn't open yet: nothing to fit
    monkeypatch.undo()
    app.windowEvent(None)  # any window event (ShowBase only minds the ones about its own window)
    region = app.cam.node().getDisplayRegion(0)
    left, right, bottom, top = (region.getLeft(), region.getRight(), region.getBottom(), region.getTop())
    width, height = app.win.getXSize() * (right - left), app.win.getYSize() * (top - bottom)
    assert width / height == pytest.approx(app_module.GAME_ASPECT, rel=0.02)
    assert app.getAspectRatio() == app_module.GAME_ASPECT
    assert math.isfinite(app.camera_view.area(0.0).top)


def test_a_debris_field_draws_its_rocks(app):
    from pewpy.game.level import parse_level

    play(app)
    app._show_background(parse_level({"background": "debris"}))
    rocks = [layer for layer in app.background.scenery.layers if layer.kind == "rock"]
    assert rocks and rocks[0].drifters
    assert app.background.root.getNumChildren() > 0
