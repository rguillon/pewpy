"""What every world's plan must be: levels the game can play."""

from pewpy.game.enemies.kinds import FINAL_BOSSES, MINI_BOSSES
from pewpy.generators.levels.plan import WorldPlan
from pewpy.scenery import params
from pewpy.scenery.params.reader import merge

LEVELS_PER_WORLD = 6


def assert_playable(world: WorldPlan) -> None:
    """Check a world: its ground a preset, its levels' sceneries read, its bosses real ones."""
    assert world.background in params.backgrounds()
    assert len(world.levels) == LEVELS_PER_WORLD
    for level in world.levels:
        assert level.mini_boss in MINI_BOSSES
        assert level.final_boss in FINAL_BOSSES
        assert level.time_of_day in params.resolve(world.background).times_of_day
        assert 0.0 <= level.clouds <= 1.0
        params.resolve(world.background, merge(world.scenery, level.scenery))
