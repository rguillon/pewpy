from pewpy.generators.models.parts.heavy_weapons import heavy_guns, heavy_missiles
from pewpy.generators.models.parts.weapons import guns


def test_the_heavy_weapons_dwarf_the_others() -> None:
    biggest_gun = max(part.extent()[1] for part in guns())
    assert all(part.extent()[1] > biggest_gun for part in heavy_guns() if part.mount == "nose")
    assert all(part.weapons for part in [*heavy_guns(), *heavy_missiles()])


def test_heavy_weapons_are_guns_and_missiles() -> None:
    assert {part.kind for part in heavy_guns()} == {"gun"}
    assert {part.kind for part in heavy_missiles()} == {"missile"}
