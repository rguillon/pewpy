from pewpy.generators.models.parts.cockpits import cockpits


def test_every_cockpit_has_glass_or_a_glowing_eye_on_top_or_the_nose() -> None:
    made = cockpits()
    assert made
    for part in made:
        assert part.kind == "cockpit"
        assert part.mount in ("top", "nose")
        glass = "c" in part.cells.values()
        eye = part.name.startswith("sensor eye")
        assert glass != eye, part.name
        if eye:
            assert "R" in part.cells.values()  # a sensor's glow: no pilot
