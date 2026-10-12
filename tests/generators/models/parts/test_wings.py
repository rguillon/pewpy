from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.parts import of_kind
from pewpy.generators.models.parts.wings import OUTLINES, RISE_SPAN, wing, wing_at


def test_a_wing_is_a_left_wing_its_root_on_the_axis() -> None:
    for part in of_kind("wing"):
        assert part.high[0] == 0
        assert any(x == 0 for x, _, _ in part.cells)


def test_every_wing_comes_in_every_size_bigger_and_bigger() -> None:
    for outline in OUTLINES:
        spans = [part.extent()[0] for part in (wing(outline, size) for size in ("tiny", "small", "medium", "huge"))]
        assert spans == sorted(spans)
    assert wing("swept", "titanic").extent()[0] > wing("swept", "giant").extent()[0]


def test_a_rising_wing_stays_one_piece_and_rises() -> None:
    gull = wing("gull", "huge")
    assert gull.high[2] > 1
    assert len(pieces(gull.cells)) == 1


def test_wings_are_made_to_any_size_rising_no_more_when_longer() -> None:
    wide = wing_at("gull", 60, 20)
    assert wide.extent()[0] == 61
    assert wide.high[2] <= round(OUTLINES["gull"][1] * RISE_SPAN)  # a long rising wing rises no more than a short one
    assert wing_at("gull", 60, 20) is wide
