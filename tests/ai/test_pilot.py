"""A brain at the controls."""

import numpy as np

from pewpy.ai.brain import Brain, parameter_count
from pewpy.ai.pilot import THINK_EVERY, Pilot, strongest
from pewpy.game.level import Level, Wave
from pewpy.game.weapons.player.arsenal import Arsenal
from pewpy.game.world import World

QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))


class Counting(Brain):
    """A brain that pushes the stick far right and counts how often it thinks."""

    thoughts = 0

    def think(self, view: np.ndarray) -> np.ndarray:  # noqa: ARG002 - it doesn't look
        self.thoughts += 1
        return np.array([5.0, -0.5, 1.0])


def test_the_strongest_weapon_is_the_highest_level_the_first_when_tied() -> None:
    arsenal = Arsenal()
    assert strongest(arsenal) == "bullets"
    arsenal.levels["missiles"] = 3
    assert strongest(arsenal) == "missiles"


def test_the_pilot_thinks_every_few_updates_holds_the_stick_and_picks_the_strongest_weapon() -> None:
    brain = Counting(np.zeros(parameter_count()))
    world = World(QUIET_LEVEL, seed=0)
    world.arsenal.levels["laser"] = 2
    pilot = Pilot(brain)
    controls = [pilot.fly(world) for _ in range(2 * THINK_EVERY)]
    assert brain.thoughts == 2
    assert controls[0].move_x == 1.0  # clamped
    assert controls[0].move_y == -0.5
    assert controls[0].fire
    assert all(each == controls[0] for each in controls)
    assert world.arsenal.selected == "laser"
