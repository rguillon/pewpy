import pytest

from pewpy.generators.models.final_bosses.attacks import ATTACKS, attack_guns


def test_every_attack_has_its_gun() -> None:
    assert set(ATTACKS) == set(attack_guns(0.5))
    assert {"aimed", "fan", "ring", "laser", "missiles"} <= set(ATTACKS)


@pytest.mark.parametrize("attack", ATTACKS)
def test_every_attack_fires_more_often_at_a_higher_difficulty(attack: str) -> None:
    easy, hard = attack_guns(0.0)[attack], attack_guns(1.0)[attack]
    assert hard.interval < easy.interval
    assert hard.count >= easy.count
    assert hard.speed >= easy.speed
