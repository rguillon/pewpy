from pewpy.game.enemies.kinds import FINAL_BOSSES, MINI_BOSSES
from pewpy.generators.levels.worlds import WORLDS


def test_the_worlds_come_in_order_each_named_once() -> None:
    assert len(WORLDS) == 8
    names = [world.name for world in WORLDS]
    assert len(set(names)) == len(names)
    assert names[0] == "Highlands"


def test_every_boss_fights_once_in_the_whole_game() -> None:
    minis = [level.mini_boss for world in WORLDS for level in world.levels]
    finals = [level.final_boss for world in WORLDS for level in world.levels]
    assert sorted(minis) == sorted(MINI_BOSSES)
    assert sorted(finals) == sorted(FINAL_BOSSES)
