from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.chain import chain, nearest
from pewpy.game.weapons.guns.gun import Gun

ORIGIN = Entity(x=0.0, y=0.0)


def test_the_nearest_target_within_reach() -> None:
    near, far = Entity(x=0.1), Entity(x=0.5)
    assert nearest(ORIGIN, [far, near]) is near
    assert nearest(ORIGIN, [far], reach=0.3) is None
    assert nearest(ORIGIN, []) is None


def test_lightning_strikes_the_nearest_then_jumps_from_each_target_to_the_next() -> None:
    first, second, third, out_of_reach = Entity(x=0.2), Entity(x=0.35), Entity(x=0.5), Entity(x=1.5)
    gun = Gun("chain", 1.0, 0.0, chain_range=0.3, chain_jump=0.2, chain_count=5)
    assert chain(gun, ORIGIN, [out_of_reach, third, first, second]) == [first, second, third]


def test_lightning_strikes_at_most_its_count_and_nothing_out_of_range() -> None:
    targets = [Entity(x=0.1 * n) for n in range(1, 6)]
    assert chain(Gun("chain", 1.0, 0.0, chain_range=0.3, chain_jump=0.2, chain_count=2), ORIGIN, targets) == targets[:2]
    assert chain(Gun("chain", 1.0, 0.0, chain_range=0.05, chain_jump=0.2, chain_count=2), ORIGIN, targets) == []
