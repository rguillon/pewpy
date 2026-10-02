"""Flying the ship with a brain: what it sees, what it decides, every THINK_EVERY updates (it holds the stick in
between, like a player's reaction time).
"""

import numpy as np

from pewpewdev.ai import sensors
from pewpewdev.ai.brain import Brain
from pewpy.game.weapons.player.arsenal import WEAPONS
from pewpy.game.world import Controls, World

THINK_EVERY = 2  # updates (at 60 per second: it decides 30 times a second)


class Pilot:
    def __init__(self, brain: Brain) -> None:
        self.brain = brain
        self.controls = Controls()
        self.wait = 0

    def fly(self, world: World) -> Controls:
        """The controls for this update; switches the weapon when the brain wants another one."""
        if self.wait > 0:
            self.wait -= 1
            return self.controls
        self.wait = THINK_EVERY - 1
        out = self.brain.think(sensors.sense(world))
        move_x, move_y = (max(-1.0, min(1.0, float(value))) for value in out[:2])
        self.controls = Controls(move_x=move_x, move_y=move_y, fire=bool(out[2] > 0))
        wanted = WEAPONS[int(np.argmax(out[3:]))]
        if wanted != world.arsenal.selected:
            world.arsenal.selected = wanted
        return self.controls
