from pewpy.generators.models.common.connect import pieces
from pewpy.generators.models.parts.connectors import STYLES, connector_at, connectors


def test_connectors_are_made_to_any_length_running_out_to_the_left() -> None:
    for style in STYLES:
        beam = connector_at(style, 30, 2)
        assert beam.extent()[0] == 30
        assert beam.high[0] == 0
        assert len(pieces(beam.cells)) == 1


def test_the_catalogs_connectors_come_in_every_style() -> None:
    made = connectors()
    assert all(part.mount == "connector" and part.kind == "connector" for part in made)
    assert len(made) >= len(STYLES)
