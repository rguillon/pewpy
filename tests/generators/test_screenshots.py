"""The Dev menu's screenshots, without the app."""

import random

import pytest

from pewpy import config
from pewpy.game.controls import Controls
from pewpy.game.level import Level, Wave
from pewpy.game.player import REGULAR_SHIPS
from pewpy.game.weapons.player.arsenal import MAX_LEVEL, WEAPONS
from pewpy.game.world import World
from pewpy.generators import screenshots
from pewpy.generators.screenshots import Shot, game_area, play, random_shot, screenshot_path, steer

QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))
BOSS_LEVEL = Level(name="boss", scroll_speed=0.2, waves=(Wave(time=1.0, enemy="harvester"),))


def test_random_shots_vary_within_their_ranges() -> None:
    rng = random.Random(4)
    shots = [random_shot(rng) for _ in range(60)]
    assert {shot.ship for shot in shots} == set(REGULAR_SHIPS)
    assert {shot.weapon for shot in shots} == set(WEAPONS)
    assert all(screenshots.LOWEST_WEAPON_LEVEL <= shot.weapon_level <= MAX_LEVEL for shot in shots)
    assert any(shot.boss for shot in shots)
    assert any(shot.secondary for shot in shots)
    assert any(shot.secondary is None for shot in shots)
    for shot in shots:
        low, high = screenshots.BOSS_TIMES if shot.boss else screenshots.TIMES
        assert low <= shot.time <= high


def test_a_shot_says_what_it_is_and_arms_the_ship() -> None:
    shot = Shot("vanguard", "laser", 4, 12.3, secondary="turret")
    assert shot.describe() == "Vanguard, laser level 4 + turret, 12 s in"
    assert (
        Shot("phantom", "bullets", 2, 3.0, boss=True).describe() == "Phantom, bullets level 2, 3 s into the boss fight"
    )
    arsenal = shot.arsenal()
    assert arsenal.selected == "laser"
    assert set(arsenal.levels.values()) == {4}
    assert arsenal.secondary is not None
    assert Shot("vanguard", "laser", 4, 1.0).arsenal().secondary is None


def test_the_ship_steers_firing_never_dies_and_gets_its_secondary_weapon_back() -> None:
    world = World(QUIET_LEVEL, seed=0)
    world.player.health = 0.1
    controls = steer(world, 0.0, "turret")
    assert controls.fire
    assert world.player.health == world.player.ship.health
    assert world.arsenal.secondary is not None
    world.player.x, world.player.y = 0.0, -0.25 * config.PLAY_HEIGHT  # on its path's point at time 0
    assert (steer(world, 0.0, None).move_x, steer(world, 0.0, None).move_y) == (0.0, 0.0)
    world.player.x = 1.0
    assert steer(world, 0.0, None).move_x == -1.0


def test_playing_to_the_moment_and_waiting_for_the_boss() -> None:
    world = World(QUIET_LEVEL, seed=0)
    world.player.invulnerable_time = 5.0
    steps: list[float] = []

    def step(controls: Controls, dt: float) -> None:
        world.update(dt, controls)
        steps.append(dt)

    play(world, Shot("vanguard", "bullets", 3, 1.0), step)
    assert sum(steps) == pytest.approx(1.0, abs=screenshots.STEP)
    assert world.player.invulnerable_time == 0.0
    boss_world = World(BOSS_LEVEL, seed=0)
    play(boss_world, Shot("vanguard", "bullets", 3, 0.5, boss=True), lambda c, dt: boss_world.update(dt, c))
    assert boss_world.boss is not None
    assert boss_world.time == pytest.approx(1.5, abs=0.1)  # the boss came at 1 s, half a second more


def test_a_boss_that_never_comes_is_given_up_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(screenshots, "LONGEST", 0.5)
    world = World(QUIET_LEVEL, seed=0)
    play(world, Shot("vanguard", "bullets", 3, 2.0, boss=True), lambda c, dt: world.update(dt, c))
    assert world.time == pytest.approx(0.5, abs=screenshots.STEP)


def test_where_screenshots_go_and_the_game_area_in_the_window() -> None:
    assert screenshot_path(0).name == "world_1.png"
    assert screenshot_path(0).parent.name == "screenshots"
    assert game_area(1000, 800, (0.0, 1.0, 0.0, 1.0)) == (0, 0, 1000, 800)
    assert game_area(1000, 800, (0.1, 0.9, 0.0, 1.0)) == (100, 0, 800, 800)  # bars on the sides
    assert game_area(1000, 800, (0.0, 1.0, 0.25, 0.75)) == (0, 200, 1000, 400)  # bars at the top and bottom
