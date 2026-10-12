from pewpy.generators.models.parts import KINDS
from pewpy.generators.models.parts.details import details

DETAILS = {"vent", "intake", "fin", "antenna", "sensor", "tank", "armor", "light", "greeble"}


def test_the_details_are_every_small_kind_of_part() -> None:
    assert {part.kind for part in details()} == DETAILS
    assert set(KINDS) >= DETAILS


def test_details_carry_no_weapons_nor_engines() -> None:
    assert not any(part.weapons or part.nozzles for part in details())
