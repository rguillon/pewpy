import numpy as np
import pytest

from pewpy.ai import sensors
from pewpy.game.entities import Bullet
from pewpy.game.level import Level, Wave
from pewpy.game.world import World

QUIET = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))


def make_world() -> World:
    return World(QUIET, seed=0)


def test_the_view_has_its_size_and_stays_in_range():
    world = make_world()
    world.enemy_bullets.append(Bullet(x=0.1, y=-0.5, vy=-0.5, hostile=True))
    view = sensors.sense(world)
    assert view.shape == (sensors.SIZE,)
    assert np.all(np.abs(view) <= 1.0 + 1e-9)


def test_with_nothing_around_every_move_is_safe():
    rooms = sensors.radar(make_world(), sensors.NO_THREATS)
    assert np.all(rooms == 1.0)


def test_a_shot_coming_down_on_the_ship_makes_staying_put_unsafe_and_a_side_step_safe():
    world = make_world()
    player = world.player
    shot = np.array([[player.x, player.y + 0.2, 0.0, -0.8, 0.02, 0.02]])
    rooms = sensors.radar(world, shot)
    moves = len(sensors.MOVES)
    stay, right = 0, 1  # MOVES: staying put first, then the directions from "right" going around
    assert rooms[moves + stay] == 0.0  # the long horizon: it hits
    assert rooms[moves + right] > 0.5
    assert sensors.safest(rooms) != sensors.MOVES[stay]


def test_the_nearest_shots_are_told_from_the_ship():
    world = make_world()
    player = world.player
    world.enemy_bullets += [
        Bullet(x=player.x + 0.3, y=player.y + 0.3, vy=-0.5, hostile=True),
        Bullet(x=player.x - 0.1, y=player.y, vx=0.4, hostile=True),
    ]
    nearest = sensors._nearest_shots(sensors._rows(world.enemy_bullets), player.x, player.y).reshape(-1, 4)
    assert nearest[0] == pytest.approx([-0.1 / sensors.SHOT_RANGE, 0.0, 0.4, 0.0])
    assert nearest[1] == pytest.approx([0.5, 0.5, 0.0, -0.5])
    assert not nearest[2:].any()  # no more shots: zeros


def test_lanes_count_what_is_above_the_ship():
    things = np.array([[-1.2, 0.5, 0, 0, 0.1, 0.1], [-1.1, 0.4, 0, 0, 0.1, 0.1], [1.2, -0.9, 0, 0, 0.1, 0.1]])
    lanes = sensors._lanes(things, above=-0.75)
    assert lanes[0] == 0.5  # two of at most four
    assert lanes[-1] == 0.0  # below the ship
