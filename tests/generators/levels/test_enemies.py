from pewpy.game.enemies.roster import ENEMY_TYPES
from pewpy.generators.levels.difficulty import MAX_DIFFICULTY
from pewpy.generators.levels.enemies import GROUND, SHAPES, UNLOCK, WARM_UP


def test_every_enemy_sent_has_shapes_and_an_unlock() -> None:
    assert set(SHAPES) == set(UNLOCK)
    assert set(UNLOCK) <= set(ENEMY_TYPES)
    assert all(UNLOCK[enemy] == 1 for enemy in WARM_UP)


def test_every_enemy_comes_at_some_difficulty_and_the_ground_ones_are_sent() -> None:
    assert all(1 <= unlock <= MAX_DIFFICULTY for unlock in UNLOCK.values())
    assert set(UNLOCK) >= GROUND


def test_every_formation_is_an_object() -> None:
    assert all(shapes and all(isinstance(shape, dict) for shape in shapes) for shapes in SHAPES.values())
