from pewpy.game.enemies.motions.track_x import TrackX
from tests.game.enemies.motions.moving import enemy, move


def test_tracking_the_players_column() -> None:
    tracker = enemy(x=0.0)
    move(tracker, TrackX(speed=0.2))
    assert tracker.vx == 0.2
    lined_up = enemy(x=0.29)
    move(lined_up, TrackX(speed=0.2))
    assert lined_up.vx == 0.0
    past = enemy(x=0.6)
    move(past, TrackX(speed=0.2))
    assert past.vx == -0.2
