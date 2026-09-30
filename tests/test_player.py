import math

import pytest

from pewpy import config
from pewpy.player import Player

DT = 1 / 60


def run(player: Player, seconds: float, move_x: float, move_y: float) -> None:
    for _ in range(round(seconds / DT)):
        player.update(DT, move_x, move_y)


def test_no_input_stays_still():
    player = Player()
    run(player, 1.0, 0, 0)
    assert (player.x, player.y) == (0.0, config.PLAYER_START_Y)


def test_has_inertia_then_reaches_full_speed():
    player = Player()
    player.update(DT, 1, 0)
    assert 0 < player.vx < config.PLAYER_SPEED
    run(player, 0.5, 1, 0)
    assert player.vx == pytest.approx(config.PLAYER_SPEED, rel=0.01)


def test_keeps_drifting_briefly_after_release():
    player = Player()
    run(player, 0.3, 1, 0)
    x_on_release = player.x
    player.update(DT, 0, 0)
    assert player.x > x_on_release


def test_diagonal_is_not_faster():
    player = Player(y=0.0)
    run(player, 0.5, 1, 1)
    assert math.hypot(player.vx, player.vy) == pytest.approx(config.PLAYER_SPEED, rel=0.01)


@pytest.mark.parametrize(("move_x", "move_y"), [(1, 0), (-1, 0), (0, 1), (0, -1)])
def test_cannot_leave_play_area(move_x, move_y):
    player = Player()
    run(player, 5.0, move_x, move_y)
    assert abs(player.x) <= (config.PLAY_WIDTH - player.width) / 2
    assert abs(player.y) <= (config.PLAY_HEIGHT - player.height) / 2
    assert abs(player.x) + abs(player.y) > 0.5  # it actually reached an edge
