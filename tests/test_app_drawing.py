"""The game app drawing a level being played: every kind of thing on screen, the effects, the HUD."""

import math
from typing import Any, cast

import pytest
from panda3d.core import ButtonThrower, KeyboardButton, ModifierButtons, MouseWatcher, NodePath

from pewpy import config
from pewpy.app import PewPewApp, bullets, drawing, keys, window
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.kinds import BOSSES, ENEMIES
from pewpy.game.enemies.roster import make_enemy
from pewpy.game.entities import Entity, Pickup
from pewpy.game.events import Event
from pewpy.game.level import parse_level
from pewpy.game.states import State
from pewpy.game.weapons.bullets import Bullet, Missile
from pewpy.game.weapons.player.arsenal import Beam
from pewpy.game.weapons.player.secondary import SecondaryWeapon
from pewpy.game.world import World
from pewpy.graphics import models


def play(app: PewPewApp, index: int = 0) -> World:
    app.states.transition(State.SHIP_SELECT)
    app.states.transition(State.WORLD_SELECT)
    app.states.transition(State.LEVEL_SELECT)
    app._start_level(index)
    assert app.world is not None
    app.world.pending_spawns = []  # only what the test puts in
    return app.world


def node(app: PewPewApp, entity: Entity) -> NodePath:
    app._sync_nodes()
    return app.nodes[entity]


def test_every_kind_of_ship_gets_its_model(app: PewPewApp) -> None:
    world = play(app)
    world.enemies = [Enemy.of_kind(kind, 0.0, 0.5) for kind in ENEMIES]
    app._sync_nodes()
    assert all(enemy in app.nodes for enemy in world.enemies)
    world.enemies = []
    app._sync_nodes()  # gone from the world: gone from the screen
    assert set(app.nodes) == {world.player}


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


@pytest.mark.parametrize(
    ("appearance", "hidden", "shade"),
    [("hidden", True, None), ("flash", False, None), ("hit", False, drawing.HIT_SHADE), ("normal", False, None)],
)
def test_enemies_show_how_they_are_doing(
    app: PewPewApp,
    monkeypatch: pytest.MonkeyPatch,
    appearance: str,
    hidden: bool,
    shade: tuple[float, float, float, float] | None,
) -> None:
    world = play(app)
    drone = Enemy.of_kind("drone", 0.0, 0.5)
    world.enemies = [drone]
    monkeypatch.setattr(drone, "appearance", lambda: appearance)
    shown = node(app, drone)
    assert shown.isHidden() is hidden
    if shade:
        assert tuple(shown.getColorScale()) == pytest.approx(shade, abs=1e-3)
    if appearance == "flash":
        assert tuple(shown.getColor()) == pytest.approx(drawing.FLASH_COLOR)


def test_a_shield_carrier_shows_its_bubble_only_while_shielded(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    world = play(app)
    carrier = Enemy.of_kind("shield_carrier", 0.0, 0.5)
    world.enemies = [carrier]
    monkeypatch.setattr(carrier, "appearance", lambda: "shield")
    assert not node(app, carrier).find("**/shield").isHidden()
    monkeypatch.setattr(carrier, "appearance", lambda: "armored")
    shown = node(app, carrier)
    assert shown.find("**/shield").isHidden()
    assert tuple(shown.getColorScale()) == pytest.approx(drawing.ARMORED_SHADE, abs=1e-3)


def moving(enemy: Enemy, vx: float, vy: float) -> Enemy:
    enemy.vx, enemy.vy = vx, vy
    return enemy


def test_enemies_turn_to_aim_or_fly(app: PewPewApp) -> None:
    world = play(app)
    world.player.x, world.player.y = 0.0, -0.5
    turret = Enemy.of_kind("turret", 0.5, 0.0)
    diver = moving(Enemy.of_kind("diver", 0.0, 0.5), 0.3, -0.3)
    diver.go_to("dive")
    swarmer = moving(Enemy.of_kind("swarmer", 0.0, 0.5), 0.4, 0.0)
    mine = Enemy.of_kind("mine", 0.0, 0.5)
    mine.age = 1.0
    world.enemies = [turret, diver, swarmer, mine]
    barrel = node(app, turret).find("**/barrel")
    assert barrel.getR() == pytest.approx(models.facing_roll(-0.5, -0.5))
    assert node(app, diver).getR() == pytest.approx(models.facing_roll(0.3, -0.3))
    assert node(app, swarmer).getR() == pytest.approx(models.facing_roll(0.4, 0.0))
    assert node(app, mine).getR() == pytest.approx(drawing.MINE_SPIN_SPEED)


def test_missiles_point_where_they_fly_and_pickups_spin(app: PewPewApp) -> None:
    world = play(app)
    missile = Missile(x=0.0, y=0.0, vx=0.5, vy=0.5)
    pickup = Pickup(x=0.2, y=0.2, kind="laser")
    world.player_bullets = [missile]
    world.pickups = [pickup]
    world.time = 1.0
    assert node(app, missile).getR() == pytest.approx(models.facing_roll(0.5, 0.5))
    assert node(app, pickup).getH() == pytest.approx(drawing.PICKUP_SPIN_SPEED)


def test_the_player_banks_blinks_and_carries_its_secondary_weapon(app: PewPewApp) -> None:
    world = play(app)
    player = world.player
    player.vx = player.ship.speed
    player.invulnerable_time = 0.15  # blinking: hidden this tenth of a second
    shown = node(app, player)
    assert shown.isHidden()
    assert shown.getH() == pytest.approx(-drawing.PLAYER_BANK_ANGLE)
    assert shown.find("secondary_turret").isHidden()
    world.arsenal.secondary = SecondaryWeapon("turret", aim_x=1.0, aim_y=0.0)
    player.invulnerable_time = 0.0
    shown = node(app, player)
    assert not shown.isHidden()
    assert not shown.find("secondary_turret").isHidden()
    assert shown.find("secondary_turret/**/barrel").getR() == pytest.approx(models.facing_roll(1.0, 0.0))
    world.arsenal.secondary = SecondaryWeapon("lightning")
    shown = node(app, player)
    assert shown.find("secondary_turret").isHidden()
    assert not shown.find("secondary_lightning").isHidden()


def test_bullets_are_sprites_colored_by_who_fired_them(app: PewPewApp) -> None:
    player_shot = Bullet(x=0.0, y=0.0, width=0.02, height=0.05)
    sniper = Bullet(x=0.0, y=0.0, hostile=True, style="sniper")
    pellet = Bullet(x=0.0, y=0.0, hostile=True, style="pellet")
    warning = Bullet(x=0.0, y=0.0, width=0.008, height=1.0, hostile=True, style="warning", harmless=True)
    assert bullets.bullet_sprite(player_shot).color == bullets.PLAYER_BULLET_COLOR
    assert bullets.bullet_sprite(sniper).color == bullets.SNIPER_BULLET_COLOR
    assert bullets.bullet_sprite(pellet).color == bullets.ENEMY_BULLET_COLOR
    assert bullets.bullet_sprite(warning).height == 1.0  # as long as the beam: only its sides glow
    world = play(app)
    world.enemy_bullets = [sniper, warning]
    app._sync_nodes()
    assert sniper not in app.nodes  # drawn as sprites, not models


def test_the_laser_beam_shows_while_firing(app: PewPewApp) -> None:
    world = play(app)
    world.laser = Beam(x=0.1, bottom=-0.5, top=0.9, width=0.05)
    world.events = [Event("burn", 0.1, 0.4)]
    (glow,) = app._laser_glows(world)
    assert glow.hits == (0.4,)
    assert not glow.hostile
    app._sync_nodes()
    assert not app.laser_node.isHidden()
    assert app.laser_node.getX() == pytest.approx(0.1)
    world.laser = None
    assert app._laser_glows(world) == []
    app._sync_nodes()
    assert app.laser_node.isHidden()


def test_enemy_beams_are_lasers_and_their_warnings_thin_red_sprites(app: PewPewApp) -> None:
    world = play(app)
    beam = Bullet(x=0.2, y=-0.3, width=0.035, height=1.6, hostile=True, style="beam", pierces=True)
    warning = Bullet(x=-0.2, y=-0.3, width=0.008, height=1.6, hostile=True, style="warning", harmless=True)
    world.enemy_bullets = [beam, warning]
    (glow,) = app._laser_glows(world)
    assert glow.hostile
    assert (glow.x, glow.top, glow.bottom) == pytest.approx((0.2, 0.5, -1.1))
    app._sync_nodes()
    assert set(app.beam_nodes) == {beam}  # a core like the player's laser
    assert app.beam_nodes[beam].getX() == pytest.approx(0.2)
    node = app.beam_nodes[beam]
    beam.x = 0.25  # a boss's beam follows it
    app._sync_nodes()
    assert app.beam_nodes[beam] is node
    assert node.getX() == pytest.approx(0.25)
    assert beam not in app.nodes
    assert warning not in app.nodes
    sprite = bullets.bullet_sprite(warning)
    assert sprite.color == bullets.WARNING_BEAM_COLOR
    assert sprite.height == warning.height
    world.enemy_bullets = []
    app._sync_nodes()
    assert app.beam_nodes == {}


def test_the_lightning_bolt_zigzags_to_what_it_struck(app: PewPewApp) -> None:
    world = play(app)
    world.bolt = [(0.0, -0.5), (0.0, -0.5), (0.3, 0.2)]  # a zero-length step too
    app._sync_nodes()
    assert app.bolt_node.getNumChildren() == 1
    world.bolt = []
    app._sync_nodes()
    assert app.bolt_node.getNumChildren() == 0


def test_every_event_plays_its_effect(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_the_letterbox_follows_the_window(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    class Sizeless:
        def hasSize(self) -> bool:  # noqa: N802 - like Panda3D's
            return False

    monkeypatch.setattr(app, "win", Sizeless())
    app._fit_letterbox()  # the window isn't open yet: nothing to fit
    monkeypatch.undo()
    app.windowEvent(cast("Any", None))  # any window event (ShowBase only minds the ones about its own window)
    region = app.cam2d.node().getDisplayRegion(0)
    left, right, bottom, top = (region.getLeft(), region.getRight(), region.getBottom(), region.getTop())
    width, height = app.win.getXSize() * (right - left), app.win.getYSize() * (top - bottom)
    assert width / height == pytest.approx(window.GAME_ASPECT, rel=0.02)
    # The 3D view is drawn at the game area's size (the test window is small enough for it).
    assert (app.scene_buffer.getXSize(), app.scene_buffer.getYSize()) == (round(width), round(height))
    app.scene_buffer.setSize(64, 64)
    app._fit_letterbox()
    assert (app.scene_buffer.getXSize(), app.scene_buffer.getYSize()) == (round(width), round(height))
    assert app.getAspectRatio() == window.GAME_ASPECT
    assert math.isfinite(app.camera_view.area(0.0).top)


def test_the_3d_view_is_drawn_at_most_so_tall() -> None:
    assert window.scene_size(1280, 1024, max_height=1440) == (1280, 1024)
    assert window.scene_size(2700, 2160, max_height=1440) == (1800, 1440)
    assert window.scene_size(0, 0) == (1, 1)


def test_a_debris_field_draws_its_rocks(app: PewPewApp) -> None:
    play(app)
    app._show_background(parse_level({"background": "debris"}))
    rocks = [layer for layer in app.background.scenery.layers if layer.kind == "rock"]
    assert rocks
    assert rocks[0].drifters
    assert app.background.root.getNumChildren() > 0
