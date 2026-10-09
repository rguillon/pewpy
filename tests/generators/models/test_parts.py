"""The catalog of built-in parts ships are made of."""

import pytest

from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.common.drawing import WEAPON_KINDS
from pewpy.generators.models.common.palette import GREYS, LIVERIES, Colors, palette
from pewpy.generators.models.parts import KINDS, MOUNTS, Part, catalog, of_kind
from pewpy.generators.models.parts.cockpits import cockpits
from pewpy.generators.models.parts.connectors import STYLES, connector_at, connectors
from pewpy.generators.models.parts.details import details
from pewpy.generators.models.parts.engines import engines
from pewpy.generators.models.parts.heavy_weapons import heavy_guns, heavy_missiles
from pewpy.generators.models.parts.hulls import PROFILES, TALLEST, hull, hull_at, hulls, thickness
from pewpy.generators.models.parts.hulls import SIZES as HULL_SIZES
from pewpy.generators.models.parts.part import Sketch
from pewpy.generators.models.parts.weapons import guns, missiles
from pewpy.generators.models.parts.wings import OUTLINES, RISE_SPAN, wing, wing_at, wings

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


def test_a_wing_is_a_left_wing_its_root_on_the_axis() -> None:
    for part in of_kind("wing"):
        assert part.high[0] == 0
        assert any(x == 0 for x, _, _ in part.cells)


def test_every_hull_and_wing_comes_in_every_size_bigger_and_bigger() -> None:
    assert len(of_kind("hull")) == len(PROFILES) * len(HULL_SIZES)
    for profile in PROFILES:
        lengths = [hull(profile, size).extent()[1] for size in HULL_SIZES]
        assert lengths == sorted(lengths)
    for outline in OUTLINES:
        spans = [part.extent()[0] for part in (wing(outline, size) for size in ("tiny", "small", "medium", "huge"))]
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


def test_a_housing_is_plated_with_lights_in_its_front_corners() -> None:
    sketch = Sketch()
    sketch.housing(2, 0, 4, 0, 1)
    assert (sketch.cells[2, 4, 1], sketch.cells[-2, 4, 1]) == ("p", "p")
    assert sketch.cells[0, 2, 1] == "k"  # a seam across its top
    assert sketch.cells[2, 0, 0] == "N"


def test_the_heavy_weapons_and_the_biggest_sizes_dwarf_the_others() -> None:
    biggest_gun = max(part.extent()[1] for part in guns())
    assert all(part.extent()[1] > biggest_gun for part in heavy_guns() if part.mount == "nose")
    assert all(part.weapons for part in [*heavy_guns(), *heavy_missiles()])
    assert wing("swept", "titanic").extent()[0] > wing("swept", "giant").extent()[0]
    assert hull("dart", "colossal").extent()[1] > hull("dart", "huge").extent()[1]


def test_hulls_and_wings_are_made_to_any_size_once() -> None:
    big = hull_at("dart", 120, 30.0, thickness(30.0))
    assert big.extent()[:2] == (61, 120)
    assert big.extent()[2] <= 2 * TALLEST + 1  # however wide, a hull stays a hull: no taller than TALLEST on top
    assert hull_at("dart", 120, 30.0, thickness(30.0)) is big  # made once
    assert len(pieces(big.cells)) == 1
    wide = wing_at("gull", 60, 20)
    assert wide.extent()[0] == 61
    assert wide.high[2] <= round(OUTLINES["gull"][1] * RISE_SPAN)  # a long rising wing rises no more than a short one
    assert hull("dart", "huge").name == "dart hull, huge"  # the catalog's sizes keep their names


def test_connectors_are_made_to_any_length_running_out_to_the_left() -> None:
    for style in STYLES:
        beam = connector_at(style, 30, 2)
        assert beam.extent()[0] == 30
        assert beam.high[0] == 0
        assert len(pieces(beam.cells)) == 1
