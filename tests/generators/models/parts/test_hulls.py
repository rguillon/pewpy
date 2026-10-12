from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.parts.hulls import PROFILES, SIZES, TALLEST, hull, hull_at, thickness


def test_every_hull_comes_in_every_size_bigger_and_bigger() -> None:
    assert len(of_kind("hull")) == len(PROFILES) * len(SIZES)
    for profile in PROFILES:
        lengths = [hull(profile, size).extent()[1] for size in SIZES]
        assert lengths == sorted(lengths)
    assert hull("dart", "colossal").extent()[1] > hull("dart", "huge").extent()[1]


def test_the_rows_of_a_hull_are_its_profile() -> None:
    part = hull("cigar", "medium")
    half, top, bottom = part.rows[part.extent()[1] // 2]
    assert half >= 1
    assert top > 0 > bottom


def test_hulls_are_made_to_any_size_once() -> None:
    big = hull_at("dart", 120, 30.0, thickness(30.0))
    assert big.extent()[:2] == (61, 120)
    assert big.extent()[2] <= 2 * TALLEST + 1  # however wide, a hull stays a hull: no taller than TALLEST on top
    assert hull_at("dart", 120, 30.0, thickness(30.0)) is big  # made once
    assert len(pieces(big.cells)) == 1
    assert hull("dart", "huge").name == "dart hull, huge"  # the catalog's sizes keep their names


def test_a_wider_hull_is_thicker_up_to_its_tallest() -> None:
    assert thickness(4.0) <= thickness(10.0) <= thickness(30.0)
    assert all(part.symmetric and part.mount == "hull" for part in of_kind("hull"))
