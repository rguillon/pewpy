import pytest

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.motions.bounce import Bounce
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.enemies.spec import EnemySpec, Part
from tests.game.enemies.motions.moving import DT, SCROLL, TARGET, enemy, move


def test_bouncing_off_the_edges() -> None:
    edge = HALF_WIDTH - 0.05
    out = enemy(x=edge + 0.01, vx=0.3)
    move(out, Bounce())
    assert out.vx == -0.3
    back = enemy(x=edge + 0.01, vx=-0.3)
    move(back, Bounce())
    assert back.vx == -0.3  # already coming back


def test_a_boss_bounces_with_its_parts_and_stays_inside() -> None:
    arm = EnemySpec(kind="arm", width=0.2)
    boss = Enemy.from_spec(EnemySpec(kind="boss", width=0.4, parts=(Part("arm", arm, 0.5, 0.0),)), x=HALF_WIDTH, y=0.5)
    boss.vx = 0.3
    Bounce(clamp=True).apply(boss, DT, TARGET, SCROLL)
    assert boss.vx == -0.3
    assert boss.x == pytest.approx(HALF_WIDTH - 0.6)
