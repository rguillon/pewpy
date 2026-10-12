import pytest

from pewpy.app import PewPewApp, bullets
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Bullet, Missile
from tests.app.driving import play


def test_bullets_are_sprites_colored_by_who_fired_them(app: PewPewApp) -> None:
    player_shot = Bullet(x=0.0, y=0.0, width=0.02, height=0.05)
    sniper = Bullet(x=0.0, y=0.0, hostile=True, style="sniper")
    pellet = Bullet(x=0.0, y=0.0, hostile=True, style="pellet")
    assert bullets.bullet_sprite(player_shot).color == bullets.PLAYER_BULLET_COLOR
    assert bullets.bullet_sprite(sniper).color == bullets.SNIPER_BULLET_COLOR
    assert bullets.bullet_sprite(pellet).color == bullets.ENEMY_BULLET_COLOR
    world = play(app)
    world.enemy_bullets = [sniper]
    app._sync_nodes()
    assert sniper not in app.nodes  # drawn as sprites, not models


def test_round_bullets_are_neither_missiles_beams_nor_warnings() -> None:
    plain = Bullet(hostile=True)
    beam = Bullet(hostile=True, style="beam")
    warning = Bullet(hostile=True, style="warning")
    assert bullets.is_round_bullet(plain)
    assert not bullets.is_round_bullet(Missile())
    assert not bullets.is_round_bullet(Entity())
    assert (bullets.is_beam(beam), bullets.is_warning(beam)) == (True, False)
    assert (bullets.is_beam(warning), bullets.is_warning(warning)) == (False, True)
    assert not bullets.is_round_bullet(beam)
    assert not bullets.is_round_bullet(warning)


def test_only_the_enemies_beams_are_beams() -> None:
    assert not bullets.is_beam(Bullet(style="beam"))
    assert not bullets.is_warning(Bullet(style="warning"))


@pytest.mark.parametrize("style", sorted(bullets.BULLET_COLORS))
def test_each_style_of_enemy_shot_has_its_color(style: str) -> None:
    assert bullets.bullet_sprite(Bullet(hostile=True, style=style)).color == bullets.BULLET_COLORS[style]


def test_a_bullets_sprite_is_its_glowing_ball_at_its_depth() -> None:
    shot = Bullet(x=0.1, y=0.2, width=0.02, height=0.05, depth=-0.03)
    sprite = bullets.bullet_sprite(shot)
    assert (sprite.x, sprite.y, sprite.depth) == (0.1, 0.2, -0.03)
    assert (sprite.width, sprite.height) == pytest.approx((0.02 * bullets.BULLET_GLOW, 0.05 * bullets.BULLET_GLOW))
    assert bullets.bullet_sprite(shot).phase == sprite.phase  # the same all its flight
