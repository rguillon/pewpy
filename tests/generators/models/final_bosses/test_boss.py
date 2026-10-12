from pewpy.generators.models.final_bosses.boss import (
    CORE,
    HEALTH,
    HEALTH_STEP,
    POINTS,
    POINTS_STEP,
    final_boss,
    part_health,
    part_points,
)

ATTACKS = ("fan", "aimed", "laser", "ring")
PARTS = (("big:cannon", -0.2, -0.1, 0.1, 0.1), ("big:cannon", 0.2, -0.1, 0.1, 0.1), ("big:turret", 0.0, 0.1, 0.1, 0.1))


def test_a_final_boss_without_parts_fights_with_its_core_only() -> None:
    spec = final_boss("BARE", "bare", 0.3, 0.2, 10, ATTACKS, ())
    assert len(spec.phases) == 2
    assert not any(phase.armored for phase in spec.phases)
    assert all(source == CORE for phase in spec.phases for source, _ in phase.guns)


def test_a_harder_boss_and_its_parts_are_tougher_and_worth_more() -> None:
    easy, hard = final_boss("A", "a", 0.3, 0.2, 1, ATTACKS, PARTS), final_boss("A", "a", 0.3, 0.2, 10, ATTACKS, PARTS)
    assert (easy.health, easy.points) == (HEALTH, POINTS + POINTS_STEP)
    assert hard.health == HEALTH + 9 * HEALTH_STEP
    assert part_health(10) > part_health(1)
    assert part_points(10) > part_points(1)
    assert hard.parts[0].health == part_health(10)


def test_parts_are_named_by_kind_and_place_the_front_ones_falling_first() -> None:
    boss = final_boss("A", "a", 0.3, 0.2, 10, ATTACKS, PARTS)
    assert [part.name for part in boss.parts] == ["cannon 1", "cannon 2", "turret 3"]
    first = boss.phases[0]
    assert set(first.until_destroyed) == {"cannon 1", "cannon 2"}  # the front ones: nearest the bottom
    assert boss.phases[-1].until_destroyed == ()
