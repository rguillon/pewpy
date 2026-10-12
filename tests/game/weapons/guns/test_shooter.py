import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.shooter import NoMakerError, Shooter


def test_a_shooter_is_an_enemy_firing_down_at_the_player_unless_told() -> None:
    piece = Entity()
    shooter = Shooter(piece, None)
    assert (shooter.hostile, shooter.forward, shooter.trigger, shooter.on_screen) == (True, -1, True, True)
    assert shooter.mounts == {}
    shooter.stop()  # standing still does nothing unless told


def test_a_shooter_cant_launch_enemies_without_something_to_make_them() -> None:
    with pytest.raises(NoMakerError, match="can't launch a 'rocket'"):
        Shooter(Entity(), None).make("rocket", 0.0, 0.0, None, None)
