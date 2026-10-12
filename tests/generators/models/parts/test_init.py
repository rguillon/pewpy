"""The catalog of built-in parts ships are made of."""

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.drawing import WEAPON_KINDS
from pewpy.generators.models.common.palette import GREYS, LIVERIES, Colors, palette
from pewpy.generators.models.parts import KINDS, MOUNTS, Part, catalog, of_kind
from pewpy.generators.models.parts.cockpits import cockpits
from pewpy.generators.models.parts.connectors import connectors
from pewpy.generators.models.parts.details import details
from pewpy.generators.models.parts.engines import engines
from pewpy.generators.models.parts.heavy_weapons import heavy_guns, heavy_missiles
from pewpy.generators.models.parts.hulls import hulls
from pewpy.generators.models.parts.weapons import guns, missiles
from pewpy.generators.models.parts.wings import wings

PARTS = list(catalog().values())


COLORS = palette(GREYS, Colors((1.0, 1.0, 1.0), "red", LIVERIES[0]))


def test_the_catalog_is_huge_and_has_every_kind_of_part_named_once() -> None:
    every = [
        *hulls(),
        *wings(),
        *connectors(),
        *cockpits(),
        *engines(),
        *guns(),
        *heavy_guns(),
        *missiles(),
        *heavy_missiles(),
        *details(),
    ]
    assert len(every) >= 400
    assert len(catalog()) == len(every)  # no two parts share a name
    assert {part.kind for part in every} == set(KINDS)
    assert [part.kind for part in PARTS] == sorted((part.kind for part in PARTS), key=list(KINDS).index)


@pytest.mark.parametrize("part", PARTS, ids=lambda part: part.name)
def test_every_part_is_one_piece_of_the_palettes_colors_mounting_a_known_way(part: Part) -> None:
    assert len(pieces(part.cells)) == 1
    assert set(part.cells.values()) <= set(COLORS)
    assert part.mount in MOUNTS
    assert part.description


@pytest.mark.parametrize("part", PARTS, ids=lambda part: part.name)
def test_every_parts_barrels_and_nozzles_are_clear(part: Part) -> None:
    for kind, x, y, z in part.weapons:
        assert kind in WEAPON_KINDS
        assert not any((x, ahead, z) in part.cells for ahead in range(y + 1, part.high[1] + 1))
    for x, y, z, width in part.nozzles:
        assert width > 0
        assert not any((round(x), behind, round(z)) in part.cells for behind in range(part.low[1], y))


def test_only_wings_and_side_parts_and_the_command_towers_are_lopsided() -> None:
    lopsided = {part.name for part in PARTS if not part.symmetric}
    assert lopsided == {
        part.name
        for part in PARTS
        if part.mount in ("wing", "side", "connector") or part.name.startswith("command tower")
    }


def test_parts_are_found_by_kind_and_mount() -> None:
    assert of_kind("engine", "pod")
    assert all(part.mount == "pod" for part in of_kind("engine", "pod"))
    assert of_kind("gun", "wing") == []


def test_the_catalog_is_made_once() -> None:
    assert catalog() is catalog()
