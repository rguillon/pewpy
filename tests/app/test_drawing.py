import pytest

from pewpy.app import PewPewApp, bullets, drawing
from pewpy.app.drawing import FLAME_FLICKER, flame_scale
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Pickup
from pewpy.game.events import Event
from pewpy.game.weapons.bullets import Bullet, Missile
from pewpy.game.weapons.player.arsenal import Beam
from pewpy.game.weapons.player.secondary import SecondaryWeapon
from pewpy.graphics import models
from tests.app.driving import node, play


def test_engine_flames_waver_and_grow_with_thrust() -> None:
    lengths = [flame_scale(time / 10, 0.0) for time in range(50)]
    assert min(lengths) < 1 < max(lengths)
    assert max(lengths) - min(lengths) <= 2 * sum(FLAME_FLICKER) + 1e-9
    assert flame_scale(0.0, 0.0, thrust=1.0) > flame_scale(0.0, 0.0) > flame_scale(0.0, 0.0, thrust=-1.0)


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


def test_enemy_beams_are_lasers_and_their_warnings_thin_red_lines_in_the_same_place(app: PewPewApp) -> None:
    world = play(app)
    beam = Bullet(x=0.2, y=-0.3, width=0.035, height=1.6, hostile=True, style="beam", pierces=True)
    warning = Bullet(x=-0.2, y=-0.3, width=0.008, height=1.6, hostile=True, style="warning", harmless=True)
    world.enemy_bullets = [beam, warning]
    (glow,) = app._laser_glows(world)
    assert glow.hostile
    assert (glow.x, glow.top, glow.bottom) == pytest.approx((0.2, 0.5, -1.1))
    app._sync_nodes()
    assert set(app.beam_nodes) == {beam, warning}  # a core like the player's laser; the warning on the same plane
    assert app.beam_nodes[beam].getX() == pytest.approx(0.2)
    lined_up = app.beam_nodes[warning]
    assert (lined_up.getX(), lined_up.getY(), lined_up.getZ()) == pytest.approx((-0.2, 0.0, -0.3))
    assert lined_up.getSz() == pytest.approx(warning.height)
    assert lined_up.getSx() == pytest.approx(warning.width * bullets.WARNING_SCALE)
    assert not bullets.is_round_bullet(warning)
    node = app.beam_nodes[beam]
    beam.x = 0.25  # a boss's beam follows it
    app._sync_nodes()
    assert app.beam_nodes[beam] is node
    assert node.getX() == pytest.approx(0.25)
    assert beam not in app.nodes
    assert warning not in app.nodes
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
