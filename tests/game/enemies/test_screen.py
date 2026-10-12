from pewpy import config
from pewpy.game.enemies.screen import BOTTOM, HALF_WIDTH, TOP


def test_the_edges_are_those_of_the_play_area_around_its_middle() -> None:
    assert TOP - BOTTOM == config.PLAY_HEIGHT
    assert TOP == -BOTTOM
    assert 2 * HALF_WIDTH == config.PLAY_WIDTH
