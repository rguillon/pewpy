from pewpy.game.bosses.catalog import FINAL_BOSSES
from pewpy.game.bosses.final_bosses import final_boss

ATTACKS = ("fan", "aimed", "laser", "ring")


def test_a_final_boss_fights_with_its_front_parts_then_its_back_ones_then_alone():
    phases = FINAL_BOSSES["avalanche"].phases
    assert phases[0].until_destroyed and phases[1].until_destroyed
    assert not phases[-1].until_destroyed


def test_without_back_parts_or_without_parts_it_skips_those_phases():
    one_kind = final_boss("solo", "solo", 0.5, 0.4, 5, ATTACKS, (("solo_gun", -0.1, 0.0, 0.1, 0.1),))
    no_parts = final_boss("bare", "bare", 0.5, 0.4, 5, ATTACKS, ())
    assert len(one_kind.phases) == len(no_parts.phases) + 1
    assert one_kind.phases[0].until_destroyed == ("gun 1",)
    assert not any(phase.until_destroyed for phase in no_parts.phases)
