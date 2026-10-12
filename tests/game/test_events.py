import dataclasses

import pytest

from pewpy.game.events import Event


def test_an_event_says_what_happened_where() -> None:
    event = Event("explosion", 0.1, 0.2, source="drone")
    assert (event.kind, event.x, event.y, event.size, event.source) == ("explosion", 0.1, 0.2, 0.0, "drone")


def test_events_are_values() -> None:
    assert Event("hurt", 0.0, 0.0) == Event("hurt", 0.0, 0.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        Event("hurt", 0.0, 0.0).x = 1.0  # ty: ignore[invalid-assignment]
