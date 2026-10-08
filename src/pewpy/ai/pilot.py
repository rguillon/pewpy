"""Flying the ship with a brain: what it sees, what it decides, every THINK_EVERY updates.

It holds the stick in between, like a player's reaction time. The weapon is a rule, not the brain's: the strongest
one (`strongest`).
"""

from pewpy.ai import sensors
from pewpy.ai.brain import Brain
from pewpy.game.controls import Controls
from pewpy.game.weapons.player.arsenal import Arsenal
from pewpy.game.world import World

THINK_EVERY = 2  # updates (at 60 per second: it decides 30 times a second)
PREFERENCE = ("bullets", "laser", "missiles")  # between weapons at the same level, the first one


def strongest(arsenal: Arsenal) -> str:
    """Return the weapon to fire: the highest level, PREFERENCE's order when tied."""
    return max(PREFERENCE, key=lambda weapon: (arsenal.levels[weapon], -PREFERENCE.index(weapon)))


class Pilot:
    """AI agent for ship navigation and combat decisions.

    AI agent for ship navigation and combat decisions.

    Attributes:
        brain (Brain): Neural network that guides decision-making
        controls (Controls): Current control state of the ship
        wait (int): Frame counter for action cooldown

    Example:
        >>> pilot = Pilot(Brain())
        >>> controls = pilot.fly(World())
        >>> print(controls)
        {'throttle': 0.8, 'fire': True, 'turn': 0.2}

    Methods:
        - fly(): Determine controls based on world state
        - __init__(): Initialize with a brain

    See Also:
        - Brain class for neural network details
        - World class for game state representation

    """

    def __init__(self, brain: Brain) -> None:
        """Initialize pilot with a neural network brain.

        Args:
            brain (Brain): Neural network that controls ship behavior

        Raises:
            ValueError: If brain is not properly initialized

        """
        self.brain = brain
        self.controls = Controls()
        self.wait = 0

    def fly(self, world: World) -> Controls:
        """Generate controls based on current world state.

        Args:
            world (World): Complete game state including ship position,
                            enemy positions, and weapon status

        Returns:
            Controls: Throttle, fire, and turn instructions

        """
        if self.wait > 0:
            self.wait -= 1
            return self.controls
        self.wait = THINK_EVERY - 1
        out = self.brain.think(sensors.sense(world))
        move_x, move_y = (max(-1.0, min(1.0, float(value))) for value in out[:2])
        self.controls = Controls(move_x=move_x, move_y=move_y, fire=bool(out[2] > 0))
        wanted = strongest(world.arsenal)
        if wanted != world.arsenal.selected:
            world.arsenal.selected = wanted
        return self.controls
