import math

import pytest

from pewpy import config
from pewpy.game.player import DEFAULT_SHIP, SHIPS, Player

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
    assert 0 < player.vx < SHIPS[DEFAULT_SHIP].speed
    run(player, 0.5, 1, 0)
    assert player.vx == pytest.approx(SHIPS[DEFAULT_SHIP].speed, rel=0.01)


def test_keeps_drifting_briefly_after_release():
    player = Player()
    run(player, 0.3, 1, 0)
    x_on_release = player.x
    player.update(DT, 0, 0)
    assert player.x > x_on_release


def test_diagonal_is_not_faster():
    player = Player(y=0.0)
    run(player, 0.5, 1, 1)
    assert math.hypot(player.vx, player.vy) == pytest.approx(SHIPS[DEFAULT_SHIP].speed, rel=0.01)


@pytest.mark.parametrize(("move_x", "move_y"), [(1, 0), (-1, 0), (0, 1), (0, -1)])
def test_cannot_leave_play_area(move_x, move_y):
    player = Player()
    run(player, 5.0, move_x, move_y)
    assert abs(player.x) <= (config.PLAY_WIDTH - player.width) / 2
    assert abs(player.y) <= (config.PLAY_HEIGHT - player.height) / 2
    assert abs(player.x) + abs(player.y) > 0.5  # it actually reached an edge


def test_the_heavy_ship_is_tougher_bigger_and_slower_and_the_light_one_the_opposite():
    normal, heavy, light = SHIPS["vanguard"], SHIPS["juggernaut"], SHIPS["phantom"]
    assert heavy.health > normal.health > light.health
    assert heavy.speed < normal.speed < light.speed
    assert heavy.size > normal.size > light.size
    assert light.regeneration > 0
    assert normal.regeneration == heavy.regeneration == 0


def test_a_ship_starts_with_its_own_health_and_size():
    player = Player(ship=SHIPS["juggernaut"])
    assert player.health == SHIPS["juggernaut"].health
    assert player.width == player.height == SHIPS["juggernaut"].size


def test_a_ship_moves_at_its_own_speed():
    heavy, light = Player(ship=SHIPS["juggernaut"]), Player(ship=SHIPS["phantom"])
    heavy.x = light.x = -config.PLAY_WIDTH / 2  # room to speed up to the right
    for _ in range(50):
        heavy.update(0.01, 1.0, 0.0)
        light.update(0.01, 1.0, 0.0)
    assert heavy.vx == pytest.approx(SHIPS["juggernaut"].speed, rel=0.01)
    assert light.vx == pytest.approx(SHIPS["phantom"].speed, rel=0.01)


def test_the_light_ship_repairs_itself_only_once_it_stopped_firing_for_a_while():
    ship = SHIPS["phantom"]
    player = Player(ship=ship)
    player.health = 1.0
    for _ in range(100):  # firing: no repair
        player.update(0.05, 0.0, 0.0, firing=True)
    assert player.health == 1.0
    player.update(ship.regeneration_delay - 0.1, 0.0, 0.0)  # not long enough since the last shot
    assert player.health == 1.0
    player.update(0.2, 0.0, 0.0)  # now it has: repairs start
    player.update(1.0, 0.0, 0.0)
    assert player.health == pytest.approx(1.0 + ship.regeneration * 1.2)
    for _ in range(100):
        player.update(0.1, 0.0, 0.0)
    assert player.health == ship.health  # up to full, no more


def test_ships_without_regeneration_never_repair():
    player = Player(ship=SHIPS["vanguard"])
    player.health = 1.0
    player.update(100.0, 0.0, 0.0)
    assert player.health == 1.0
