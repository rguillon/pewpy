"""The catalog of built-in parts ships are made of."""

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.drawing import WEAPON_KINDS
from pewpy.generators.models.common.palette import GREYS, LIVERIES, Colors, palette
from pewpy.generators.models.ships.parts import KINDS, MOUNTS, Part, catalog, of_kind
from pewpy.generators.models.ships.parts.cockpits import cockpits
from pewpy.generators.models.ships.parts.details import details, equipment
from pewpy.generators.models.ships.parts.engines import engines
from pewpy.generators.models.ships.parts.hulls import PROFILES, SIZES, hull, hulls
from pewpy.generators.models.ships.parts.weapons import guns, missiles
from pewpy.generators.models.ships.parts.wings import OUTLINES, wing, wings

PARTS = list(catalog().values())
COLORS = palette(GREYS, Colors((1.0, 1.0, 1.0), "red", LIVERIES[0]))


def test_the_catalog_is_huge_and_has_every_kind_of_part_named_once() -> None:
    every = [*hulls(), *wings(), *cockpits(), *engines(), *guns(), *missiles(), *details(), *equipment()]
    assert len(every) >= 300
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
        part.name for part in PARTS if part.mount in ("wing", "side") or part.name.startswith("command tower")
    }


def test_a_wing_is_a_left_wing_its_root_on_the_axis() -> None:
    for part in of_kind("wing"):
        assert part.high[0] == 0
        assert any(x == 0 for x, _, _ in part.cells)


def test_every_hull_and_wing_comes_in_every_size_bigger_and_bigger() -> None:
    assert len(of_kind("hull")) == len(PROFILES) * len(SIZES)
    for name in PROFILES:
        lengths = [hull(name, size).extent()[1] for size in SIZES]
        assert lengths == sorted(lengths)
    for name in OUTLINES:
        spans = [part.extent()[0] for part in (wing(name, size) for size in ("tiny", "small", "medium", "huge"))]
        assert spans == sorted(spans)


def test_a_rising_wing_stays_one_piece_and_rises() -> None:
    gull = wing("gull", "huge")
    assert gull.high[2] > 1
    assert len(pieces(gull.cells)) == 1


def test_parts_are_found_by_kind_and_mount() -> None:
    assert of_kind("engine", "pod")
    assert all(part.mount == "pod" for part in of_kind("engine", "pod"))
    assert of_kind("gun", "wing") == []


def test_the_rows_of_a_hull_are_its_profile() -> None:
    part = hull("cigar", "medium")
    half, top, bottom = part.rows[part.extent()[1] // 2]
    assert half >= 1
    assert top > 0 > bottom
