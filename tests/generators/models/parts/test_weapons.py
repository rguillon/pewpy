from pewpy.generators.models.common.drawing import WEAPON_KINDS
from pewpy.generators.models.parts.weapons import guns, missiles


def test_every_gun_and_launcher_has_its_barrels() -> None:
    for part in [*guns(), *missiles()]:
        assert part.weapons, part.name
        assert all(kind in WEAPON_KINDS for kind, _, _, _ in part.weapons)


def test_guns_are_guns_and_missiles_missiles() -> None:
    assert {part.kind for part in guns()} == {"gun"}
    assert {part.kind for part in missiles()} == {"missile"}
    assert {kind for part in missiles() for kind, _, _, _ in part.weapons} == {"missile"}
