from pewpy.generators.models.parts.engines import engines


def test_every_engine_has_its_nozzles_on_its_back() -> None:
    made = engines()
    assert made
    for part in made:
        assert part.kind == "engine"
        assert part.nozzles, part.name
        assert {y for _, y, _, _ in part.nozzles} == {part.low[1]}, part.name


def test_engines_mount_on_the_tail_or_as_pods() -> None:
    assert {part.mount for part in engines()} == {"tail", "pod"}
