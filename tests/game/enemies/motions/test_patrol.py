from pewpy.game.enemies.motions.patrol import Patrol
from tests.game.enemies.motions.moving import enemy, move


def test_patrolling_starts_towards_the_middle() -> None:
    left, right = enemy(x=-0.5), enemy(x=0.5)
    move(left, Patrol(speed=0.1))
    move(right, Patrol(speed=0.1))
    assert (left.vx, right.vx) == (0.1, -0.1)
    going = enemy(x=0.5, vx=0.2)
    move(going, Patrol(speed=0.1))
    assert going.vx == 0.2  # already moving sideways: left alone
