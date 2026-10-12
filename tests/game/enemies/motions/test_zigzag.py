from pewpy.game.enemies.motions.zigzag import Zigzag
from tests.game.enemies.motions.moving import DT, SCROLL, TARGET, enemy


def test_zigzagging_first_towards_the_player() -> None:
    hornet = enemy(x=0.0)
    Zigzag(speed=0.35, every=0.6).apply(hornet, DT, TARGET, SCROLL)
    assert hornet.vx == -0.35  # it turned at once: away from the player, at x 0.3
    for _ in range(round(0.6 / DT) + 1):
        Zigzag(speed=0.35, every=0.6).apply(hornet, DT, TARGET, SCROLL)
    assert hornet.vx == 0.35
    leftwards = enemy(x=0.5)
    Zigzag(speed=0.35, every=0.6).apply(leftwards, DT, TARGET, SCROLL)
    assert leftwards.vx == 0.35
