import math
from dataclasses import replace

import pytest

from pewpy import config
from pewpy.game.level import Level
from pewpy.game.player import DEFAULT_SHIP, REGULAR_SHIPS, SHIPS, Player
from pewpy.game.weapons.player.arsenal import MAX_LEVEL, WEAPONS
from pewpy.game.world import World

DT = 1 / 60


def run(player: Player, seconds: float, move_x: float, move_y: float) -> None:
    for _ in range(round(seconds / DT)):
        player.update(DT, move_x, move_y)


def test_no_input_stays_still() -> None:
    player = Player()
    run(player, 1.0, 0, 0)
    assert (player.x, player.y) == (0.0, config.PLAYER_START_Y)


def test_has_inertia_then_reaches_full_speed() -> None:
    player = Player()
    player.update(DT, 1, 0)
    assert 0 < player.vx < SHIPS[DEFAULT_SHIP].speed
    run(player, 0.5, 1, 0)
    assert player.vx == pytest.approx(SHIPS[DEFAULT_SHIP].speed, rel=0.01)


def test_keeps_drifting_briefly_after_release() -> None:
    player = Player()
    run(player, 0.3, 1, 0)
    x_on_release = player.x
    player.update(DT, 0, 0)
    assert player.x > x_on_release


def test_diagonal_is_not_faster() -> None:
    player = Player(y=0.0)
    run(player, 0.5, 1, 1)
    assert math.hypot(player.vx, player.vy) == pytest.approx(SHIPS[DEFAULT_SHIP].speed, rel=0.01)


@pytest.mark.parametrize(("move_x", "move_y"), [(1, 0), (-1, 0), (0, 1), (0, -1)])
def test_cannot_leave_play_area(move_x: float, move_y: float) -> None:
    player = Player()
    run(player, 5.0, move_x, move_y)
    assert abs(player.x) <= (config.PLAY_WIDTH - player.width) / 2
    assert abs(player.y) <= (config.PLAY_HEIGHT - player.height) / 2
    assert abs(player.x) + abs(player.y) > 0.5  # it actually reached an edge


def test_the_heavy_ship_is_tougher_bigger_and_slower_and_the_light_one_the_opposite() -> None:
    normal, heavy, light = SHIPS["vanguard"], SHIPS["juggernaut"], SHIPS["phantom"]
    assert heavy.health > normal.health > light.health
    assert heavy.speed < normal.speed < light.speed
    assert heavy.size > normal.size > light.size
    assert light.regeneration > normal.regeneration > heavy.regeneration > 0  # every ship repairs itself


def test_a_ship_starts_with_its_own_health_and_size() -> None:
    player = Player(ship=SHIPS["juggernaut"])
    assert player.health == SHIPS["juggernaut"].health
    assert player.width == player.height == SHIPS["juggernaut"].size


def test_a_ship_moves_at_its_own_speed() -> None:
    heavy, light = Player(ship=SHIPS["juggernaut"]), Player(ship=SHIPS["phantom"])
    heavy.x = light.x = -config.PLAY_WIDTH / 2  # room to speed up to the right
    for _ in range(50):
        heavy.update(0.01, 1.0, 0.0)
        light.update(0.01, 1.0, 0.0)
    assert heavy.vx == pytest.approx(SHIPS["juggernaut"].speed, rel=0.01)
    assert light.vx == pytest.approx(SHIPS["phantom"].speed, rel=0.01)


@pytest.mark.parametrize("key", [key for key, ship in SHIPS.items() if ship.regeneration])
def test_a_ship_repairs_itself_only_once_it_stopped_firing_for_a_while(key: str) -> None:
    ship = SHIPS[key]
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
    for _ in range(1000):
        player.update(0.1, 0.0, 0.0)
    assert player.health == ship.health  # up to full, no more


def test_ships_without_regeneration_never_repair() -> None:
    player = Player(ship=replace(SHIPS["vanguard"], regeneration=0.0))
    player.health = 1.0
    player.update(100.0, 0.0, 0.0)
    assert player.health == 1.0


def test_a_test_ship_starts_fully_armed_and_isnt_a_regular_ship() -> None:
    tester = replace(SHIPS[DEFAULT_SHIP], health=99999.0, full_arsenal=True, test=True)
    world = World(Level(name="test", scroll_speed=0.2, waves=()), ship=tester)
    assert world.arsenal.levels == dict.fromkeys(WEAPONS, MAX_LEVEL)
    assert world.player.health == 99999.0
    assert World(Level(name="test", scroll_speed=0.2, waves=())).arsenal.levels == dict.fromkeys(WEAPONS, 1)
    assert all(not ship.test for ship in REGULAR_SHIPS.values())
    assert set(REGULAR_SHIPS) == {key for key, ship in SHIPS.items() if not ship.test}
