import numpy as np

from pewpy.ai import pilot as pilot_module
from pewpy.ai.brain import Brain, parameter_count
from pewpy.ai.pilot import Pilot
from pewpy.game.level import Level, Wave
from pewpy.game.world import World

QUIET = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))


def brain_wanting(move_x: float, move_y: float, fire: float, weapon: int) -> Brain:
    """A brain that ignores what it sees: only its last layer's biases."""
    brain = Brain(np.zeros(parameter_count()))
    biases = brain.layers[-2][-1]  # the output layer's biases (the direct path comes last)
    biases[:3] = (move_x, move_y, fire)
    biases[3 + weapon] = 1.0
    return brain


def test_the_pilot_flies_as_the_brain_wants_and_holds_the_stick_between_thoughts():
    world = World(QUIET, seed=0)
    pilot = Pilot(brain_wanting(3.0, -0.5, 1.0, weapon=2))
    controls = pilot.fly(world)
    assert (controls.move_x, controls.move_y, controls.fire) == (1.0, -0.5, True)  # the stick stops at 1
    assert world.arsenal.selected == "missiles"
    pilot.brain = brain_wanting(0.0, 0.0, -1.0, weapon=0)
    for _ in range(pilot_module.THINK_EVERY - 1):
        assert pilot.fly(world) == controls  # still the last decision
    assert pilot.fly(world).fire is False
    assert world.arsenal.selected == "bullets"
