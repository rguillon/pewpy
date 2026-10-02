"""The final bosses: one at the end of each level, after its mini boss (02-enemies-bosses.md). Placeholders.

Each is a big core (a boss candidate, see pewpewdev/tools/make_boss_candidates.py) with its parts, and four attacks. Its
phases come from them (see `final_boss`): the front parts first, then the back ones, while the core is armored;
then the core, then the core in a rage. Everything gets harder with the level's difficulty (1 to 20).
"""

from dataclasses import replace

from pewpy.game.bosses import CORE, BossSpec, Gun, PartSpec, Phase

PartPlan = tuple[str, float, float, float, float]  # drawing, x, y, width, height (from the core's middle)


def attack_guns(p: float) -> dict[str, Gun]:
    """Each attack's gun, at `p` from 0 (difficulty 1) to 1 (difficulty 20)."""
    return {
        "aimed": Gun("aimed", 1.6 - 0.5 * p, 0.6 + 0.15 * p, volley=3 + round(2 * p), gap=0.12, style="heavy"),
        "sniper": Gun("aimed", 1.5 - 0.4 * p, 0.85 + 0.1 * p, volley=2 + round(2 * p), gap=0.2, style="sniper"),
        "fan": Gun("fan", 1.8 - 0.5 * p, 0.45 + 0.1 * p, count=5 + round(4 * p), spread=12, sweep=25),
        "ring": Gun("ring", 2.0 - 0.6 * p, 0.38 + 0.08 * p, count=12 + round(8 * p), turn=9),
        "spiral": Gun("ring", 0.16 - 0.04 * p, 0.42 + 0.06 * p, count=2 + round(2 * p), turn=13),
        "wave": Gun("fan", 1.6 - 0.4 * p, 0.45 + 0.1 * p, count=3 + round(2 * p), spread=20, style="wave"),
        "accel": Gun("aimed", 1.8 - 0.5 * p, 0.55 + 0.15 * p, count=5, spread=8, style="accel"),
        "curve": Gun("ring", 1.8 - 0.5 * p, 0.35 + 0.05 * p, count=8 + round(4 * p), curve=35, style="curve"),
        "pellets": Gun("aimed", 1.6 - 0.4 * p, 0.6 + 0.1 * p, count=7 + round(4 * p), spread=6, style="pellet"),
        "laser": Gun("laser", 4.5 - 1.5 * p, 0.0, width=0.07, duration=1.0 + 0.4 * p),
        "missiles": Gun("aimed", 3.5 - 1.0 * p, 0.0, count=2, spread=40, projectile="missile"),
        "rockets": Gun("fan", 2.6 - 0.8 * p, 0.0, count=3, spread=25, projectile="rocket"),
        "cluster": Gun("fan", 3.0 - 0.8 * p, 0.0, count=2 + round(p), spread=30, projectile="cluster"),
    }


ATTACKS = tuple(attack_guns(0.0))


def final_boss(
    name: str,
    drawing: str,
    width: float,
    height: float,
    difficulty: int,
    attacks: tuple[str, ...],
    parts: tuple[PartPlan, ...],
) -> BossSpec:
    """A final boss of a level of `difficulty`: its health, points and phases from it and its four attacks.

    attacks: the front parts', the back parts', the core's, and the one it adds in its rage (the last phase). The
    front parts are the drawings nearest the bottom of the screen (half of the kinds of parts), the back ones the
    others. A "laser" on the core fires two beams apart.
    """
    p = (difficulty - 1) / 19
    guns = attack_guns(p)
    front_attack, back_attack, core_attack, rage_attack = attacks
    kinds = sorted({plan[0] for plan in parts}, key=lambda kind: sum(plan[2] for plan in parts if plan[0] == kind))
    front_kinds = set(kinds[: (len(kinds) + 1) // 2])
    specs = tuple(
        PartSpec(
            f"{part_drawing.rsplit('_', 1)[-1]} {index + 1}",
            part_drawing,
            x,
            y,
            part_width,
            part_height,
            round(16 + 1.6 * (difficulty - 1)),
            300 + 30 * difficulty,
        )
        for index, (part_drawing, x, y, part_width, part_height) in enumerate(parts)
    )
    front = tuple(spec.name for spec in specs if spec.drawing in front_kinds)
    back = tuple(spec.name for spec in specs if spec.drawing not in front_kinds)

    def from_parts(names: tuple[str, ...], attack: str) -> tuple[tuple[str, Gun], ...]:
        """Every part of `names` firing `attack` in turn (as often in all as about two parts would)."""
        interval = guns[attack].interval * max(1.0, len(names) / 2) ** 0.5
        return tuple(
            (part, replace(guns[attack], interval=interval, delay=interval * index / len(names)))
            for index, part in enumerate(names)
        )

    def from_core(attack: str, delay: float = 0.0) -> tuple[str, Gun]:
        offsets = (-width / 4, width / 4) if attack == "laser" else (0.0,)
        return CORE, replace(guns[attack], delay=delay, offsets=offsets)

    sway = 0.08 + 0.004 * difficulty
    phases = []
    if front:
        core_guns = (from_core("aimed", 0.8),) if difficulty >= 8 else ()
        phases.append(Phase(from_parts(front, front_attack) + core_guns, sway, armored=True, until_destroyed=front))
    if back:
        phases.append(
            Phase(
                (*from_parts(back, back_attack), from_core(core_attack, 0.6)), sway, armored=True, until_destroyed=back
            )
        )
    phases.append(Phase((from_core(core_attack), from_core(rage_attack, 0.9)), sway + 0.03, until_below=0.5))
    rage = (
        from_core(rage_attack),
        from_core(front_attack, 0.5),
        from_core("spiral" if difficulty >= 6 else "ring", 1.0),
    )
    phases.append(Phase(rage, sway + 0.06))
    return BossSpec(
        name=name,
        drawing=drawing,
        width=width,
        height=height,
        health=float(110 + 14 * (difficulty - 1)),
        points=4000 + 400 * difficulty,
        phases=tuple(phases),
        parts=specs,
    )


FINAL_BOSSES: dict[str, BossSpec] = {
    # 1-1: boss candidate #167.
    "avalanche": final_boss(
        "AVALANCHE",
        "avalanche",
        0.5,
        0.287,
        1,
        ("fan", "aimed", "laser", "ring"),
        (
            ("avalanche_a", -0.133, -0.027, 0.127, 0.14),
            ("avalanche_a", 0.133, -0.027, 0.127, 0.14),
            ("avalanche_b", -0.107, 0.04, 0.113, 0.133),
            ("avalanche_b", 0.107, 0.04, 0.113, 0.133),
            ("avalanche_c", -0.207, -0.04, 0.087, 0.093),
            ("avalanche_c", 0.207, -0.04, 0.087, 0.093),
        ),
    ),
    # 1-2: boss candidate #187.
    "frostjaw": final_boss(
        "FROSTJAW",
        "frostjaw",
        0.513,
        0.287,
        2,
        ("pellets", "fan", "wave", "ring"),
        (
            ("frostjaw_a", -0.107, 0.013, 0.113, 0.14),
            ("frostjaw_a", 0.107, 0.013, 0.113, 0.14),
            ("frostjaw_b", -0.033, -0.093, 0.18, 0.167),
            ("frostjaw_b", 0.033, -0.093, 0.18, 0.167),
            ("frostjaw_c", -0.227, 0.027, 0.127, 0.147),
            ("frostjaw_c", 0.227, 0.027, 0.127, 0.147),
            ("frostjaw_d", -0.04, -0.02, 0.113, 0.1),
            ("frostjaw_d", 0.04, -0.02, 0.113, 0.1),
        ),
    ),
    # 1-3: boss candidate #070.
    "iron_summit": final_boss(
        "IRON SUMMIT",
        "iron_summit",
        0.547,
        0.313,
        3,
        ("aimed", "rockets", "laser", "fan"),
        (
            ("iron_summit_a", -0.263, 0.04, 0.113, 0.113),
            ("iron_summit_b", -0.037, -0.007, 0.14, 0.187),
            ("iron_summit_c", -0.183, 0.067, 0.153, 0.26),
            ("iron_summit_c", 0.183, 0.067, 0.153, 0.26),
        ),
    ),
    # 1-4: boss candidate #179.
    "stormpeak": final_boss(
        "STORMPEAK",
        "stormpeak",
        0.54,
        0.327,
        4,
        ("wave", "ring", "curve", "spiral"),
        (
            ("stormpeak_a", -0.04, 0.0, 0.127, 0.24),
            ("stormpeak_a", 0.04, 0.0, 0.127, 0.24),
            ("stormpeak_b", -0.053, -0.073, 0.14, 0.207),
            ("stormpeak_b", 0.053, -0.073, 0.14, 0.207),
            ("stormpeak_c", -0.08, 0.08, 0.14, 0.18),
            ("stormpeak_c", 0.08, 0.08, 0.14, 0.18),
            ("stormpeak_d", -0.16, -0.053, 0.167, 0.213),
            ("stormpeak_d", 0.16, -0.053, 0.167, 0.213),
            ("stormpeak_e", 0.0, -0.04, 0.14, 0.16),
        ),
    ),
    # 1-5: boss candidate #064.
    "ridgebreaker": final_boss(
        "RIDGEBREAKER",
        "ridgebreaker",
        0.5,
        0.353,
        5,
        ("rockets", "pellets", "laser", "fan"),
        (
            ("ridgebreaker_a", -0.147, -0.007, 0.167, 0.193),
            ("ridgebreaker_b", -0.06, 0.013, 0.113, 0.127),
            ("ridgebreaker_c", -0.027, -0.107, 0.1, 0.147),
            ("ridgebreaker_c", 0.027, -0.107, 0.1, 0.147),
            ("ridgebreaker_d", -0.16, -0.1, 0.113, 0.147),
            ("ridgebreaker_e", 0.16, -0.1, 0.113, 0.147),
        ),
    ),
    # 1-6: boss candidate #068.
    "highlord": final_boss(
        "HIGHLORD",
        "highlord",
        0.567,
        0.327,
        6,
        ("aimed", "cluster", "laser", "curve"),
        (
            ("highlord_a", -0.113, 0.1, 0.14, 0.12),
            ("highlord_a", 0.113, 0.1, 0.14, 0.12),
            ("highlord_b", -0.14, 0.013, 0.167, 0.147),
            ("highlord_b", 0.14, 0.013, 0.167, 0.147),
            ("highlord_c", -0.027, 0.14, 0.1, 0.14),
            ("highlord_c", 0.027, 0.14, 0.1, 0.14),
            ("highlord_d", 0.0, -0.033, 0.1, 0.153),
        ),
    ),
    # 2-1: boss candidate #063.
    "ironbark": final_boss(
        "IRONBARK",
        "ironbark",
        0.5,
        0.373,
        3,
        ("fan", "accel", "ring", "pellets"),
        (
            ("ironbark_a", -0.033, 0.163, 0.113, 0.1),
            ("ironbark_a", 0.033, 0.163, 0.113, 0.1),
            ("ironbark_b", -0.133, -0.137, 0.127, 0.113),
            ("ironbark_b", 0.133, -0.137, 0.127, 0.113),
            ("ironbark_c", -0.22, -0.11, 0.153, 0.16),
            ("ironbark_c", 0.22, -0.11, 0.153, 0.16),
            ("ironbark_d", -0.06, 0.063, 0.167, 0.173),
            ("ironbark_d", 0.06, 0.063, 0.167, 0.173),
            ("ironbark_e", -0.12, -0.057, 0.153, 0.153),
            ("ironbark_e", 0.12, -0.057, 0.153, 0.153),
            ("ironbark_f", 0.0, -0.05, 0.113, 0.107),
        ),
    ),
    # 2-2: boss candidate #163.
    "thornback": final_boss(
        "THORNBACK",
        "thornback",
        0.5,
        0.393,
        4,
        ("pellets", "curve", "laser", "wave"),
        (
            ("thornback_a", -0.073, -0.027, 0.113, 0.213),
            ("thornback_a", 0.073, -0.027, 0.113, 0.213),
            ("thornback_b", -0.193, -0.033, 0.113, 0.16),
            ("thornback_b", 0.193, -0.033, 0.113, 0.16),
            ("thornback_c", 0.0, 0.02, 0.14, 0.127),
        ),
    ),
    # 2-3: boss candidate #040.
    "rootmaw": final_boss(
        "ROOTMAW",
        "rootmaw",
        0.68,
        0.293,
        5,
        ("rockets", "wave", "accel", "spiral"),
        (
            ("rootmaw_a", -0.21, -0.123, 0.193, 0.2),
            ("rootmaw_b", 0.21, -0.123, 0.193, 0.2),
            ("rootmaw_c", -0.23, 0.083, 0.14, 0.133),
            ("rootmaw_d", 0.23, 0.083, 0.14, 0.133),
            ("rootmaw_e", -0.063, 0.05, 0.193, 0.273),
            ("rootmaw_e", 0.063, 0.05, 0.193, 0.273),
            ("rootmaw_f", -0.297, -0.043, 0.207, 0.187),
        ),
    ),
    # 2-4: boss candidate #034.
    "wildfire": final_boss(
        "WILDFIRE",
        "wildfire",
        0.54,
        0.373,
        6,
        ("accel", "fan", "laser", "curve"),
        (
            ("wildfire_a", -0.107, 0.11, 0.1, 0.113),
            ("wildfire_a", 0.107, 0.11, 0.1, 0.113),
            ("wildfire_b", -0.093, 0.01, 0.127, 0.14),
            ("wildfire_c", -0.1, -0.15, 0.087, 0.127),
            ("wildfire_d", -0.26, -0.063, 0.14, 0.16),
            ("wildfire_e", -0.18, -0.077, 0.087, 0.147),
        ),
    ),
    # 2-5: boss candidate #002.
    "grovekeeper": final_boss(
        "GROVEKEEPER",
        "grovekeeper",
        0.553,
        0.367,
        7,
        ("curve", "missiles", "ring", "laser"),
        (
            ("grovekeeper_a", -0.06, 0.107, 0.1, 0.167),
            ("grovekeeper_a", 0.06, 0.107, 0.1, 0.167),
            ("grovekeeper_b", -0.073, -0.073, 0.1, 0.087),
            ("grovekeeper_b", 0.073, -0.073, 0.1, 0.087),
            ("grovekeeper_c", -0.14, 0.167, 0.167, 0.167),
            ("grovekeeper_c", 0.14, 0.167, 0.167, 0.167),
            ("grovekeeper_d", -0.087, 0.02, 0.073, 0.093),
            ("grovekeeper_d", 0.087, 0.02, 0.073, 0.093),
            ("grovekeeper_e", -0.253, 0.007, 0.14, 0.227),
            ("grovekeeper_e", 0.253, 0.007, 0.14, 0.227),
            ("grovekeeper_f", 0.0, -0.02, 0.087, 0.113),
        ),
    ),
    # 2-6: boss candidate #131.
    "old_growth": final_boss(
        "OLD GROWTH",
        "old_growth",
        0.553,
        0.367,
        8,
        ("wave", "rockets", "laser", "accel"),
        (
            ("old_growth_a", -0.213, 0.033, 0.14, 0.133),
            ("old_growth_a", 0.213, 0.033, 0.14, 0.133),
            ("old_growth_b", -0.1, -0.053, 0.113, 0.12),
            ("old_growth_b", 0.1, -0.053, 0.113, 0.12),
            ("old_growth_c", -0.107, 0.027, 0.1, 0.127),
            ("old_growth_c", 0.107, 0.027, 0.1, 0.127),
        ),
    ),
    # 3-1: boss candidate #099.
    "bogmaw": final_boss(
        "BOGMAW",
        "bogmaw",
        0.527,
        0.387,
        5,
        ("wave", "pellets", "curve", "ring"),
        (
            ("bogmaw_a", -0.06, -0.05, 0.113, 0.133),
            ("bogmaw_a", 0.06, -0.05, 0.113, 0.133),
            ("bogmaw_b", -0.047, -0.17, 0.127, 0.14),
            ("bogmaw_b", 0.047, -0.17, 0.127, 0.14),
            ("bogmaw_c", -0.253, 0.11, 0.087, 0.107),
            ("bogmaw_c", 0.253, 0.11, 0.087, 0.107),
        ),
    ),
    # 3-2: boss candidate #085.
    "mirelord": final_boss(
        "MIRELORD",
        "mirelord",
        0.52,
        0.4,
        6,
        ("missiles", "fan", "laser", "wave"),
        (
            ("mirelord_a", -0.03, -0.083, 0.14, 0.153),
            ("mirelord_b", -0.037, 0.137, 0.1, 0.147),
            ("mirelord_b", 0.037, 0.137, 0.1, 0.147),
            ("mirelord_c", -0.17, -0.017, 0.153, 0.213),
            ("mirelord_c", 0.17, -0.017, 0.153, 0.213),
            ("mirelord_d", -0.11, 0.15, 0.14, 0.24),
            ("mirelord_e", 0.003, 0.01, 0.087, 0.127),
        ),
    ),
    # 3-3: boss candidate #165.
    "fenwraith": final_boss(
        "FENWRAITH",
        "fenwraith",
        0.513,
        0.413,
        7,
        ("curve", "accel", "wave", "spiral"),
        (
            ("fenwraith_a", -0.04, -0.03, 0.167, 0.24),
            ("fenwraith_a", 0.04, -0.03, 0.167, 0.24),
            ("fenwraith_b", -0.053, 0.177, 0.113, 0.16),
            ("fenwraith_b", 0.053, 0.177, 0.113, 0.16),
            ("fenwraith_c", 0.0, -0.037, 0.153, 0.167),
        ),
    ),
    # 3-4: boss candidate #138.
    "hydra": final_boss(
        "HYDRA",
        "hydra",
        0.58,
        0.373,
        8,
        ("wave", "cluster", "laser", "curve"),
        (
            ("hydra_a", -0.087, 0.097, 0.127, 0.193),
            ("hydra_b", -0.207, -0.123, 0.127, 0.247),
            ("hydra_b", 0.207, -0.123, 0.127, 0.247),
            ("hydra_c", -0.08, -0.023, 0.087, 0.14),
            ("hydra_c", 0.08, -0.023, 0.087, 0.14),
        ),
    ),
    # 3-5: boss candidate #028.
    "marsh_titan": final_boss(
        "MARSH TITAN",
        "marsh_titan",
        0.607,
        0.373,
        9,
        ("pellets", "missiles", "accel", "laser"),
        (
            ("marsh_titan_a", -0.127, -0.077, 0.153, 0.213),
            ("marsh_titan_a", 0.127, -0.077, 0.153, 0.213),
            ("marsh_titan_b", -0.207, 0.063, 0.14, 0.12),
            ("marsh_titan_b", 0.207, 0.063, 0.14, 0.12),
            ("marsh_titan_c", -0.233, 0.177, 0.153, 0.187),
            ("marsh_titan_c", 0.233, 0.177, 0.153, 0.187),
            ("marsh_titan_d", -0.247, -0.03, 0.1, 0.093),
            ("marsh_titan_d", 0.247, -0.03, 0.1, 0.093),
            ("marsh_titan_e", 0.0, -0.063, 0.14, 0.207),
        ),
    ),
    # 3-6: boss candidate #109.
    "drowned_king": final_boss(
        "DROWNED KING",
        "drowned_king",
        0.567,
        0.427,
        10,
        ("curve", "wave", "laser", "missiles"),
        (
            ("drowned_king_a", -0.053, 0.01, 0.153, 0.22),
            ("drowned_king_a", 0.053, 0.01, 0.153, 0.22),
            ("drowned_king_b", -0.233, 0.03, 0.127, 0.167),
            ("drowned_king_b", 0.233, 0.03, 0.127, 0.167),
            ("drowned_king_c", -0.133, -0.057, 0.14, 0.12),
            ("drowned_king_c", 0.133, -0.057, 0.14, 0.12),
            ("drowned_king_d", -0.207, -0.07, 0.14, 0.227),
            ("drowned_king_d", 0.207, -0.07, 0.14, 0.227),
            ("drowned_king_e", 0.0, -0.057, 0.153, 0.28),
        ),
    ),
    # 4-1: boss candidate #042.
    "scarecrow": final_boss(
        "SCARECROW",
        "scarecrow",
        0.64,
        0.4,
        7,
        ("pellets", "rockets", "fan", "laser"),
        (
            ("scarecrow_a", -0.283, 0.063, 0.087, 0.093),
            ("scarecrow_b", 0.283, 0.063, 0.087, 0.093),
            ("scarecrow_c", -0.217, -0.043, 0.113, 0.153),
            ("scarecrow_d", -0.29, -0.197, 0.1, 0.127),
            ("scarecrow_e", -0.043, 0.083, 0.127, 0.16),
            ("scarecrow_f", -0.177, 0.063, 0.167, 0.213),
            ("scarecrow_g", -0.023, -0.083, 0.087, 0.107),
            ("scarecrow_g", 0.023, -0.083, 0.087, 0.107),
        ),
    ),
    # 4-2: boss candidate #074.
    "combine": final_boss(
        "COMBINE",
        "combine",
        0.673,
        0.387,
        8,
        ("fan", "accel", "laser", "cluster"),
        (
            ("combine_a", -0.267, -0.083, 0.22, 0.233),
            ("combine_a", 0.267, -0.083, 0.22, 0.233),
            ("combine_b", -0.053, 0.157, 0.207, 0.193),
            ("combine_b", 0.053, 0.157, 0.207, 0.193),
            ("combine_c", -0.147, 0.037, 0.14, 0.133),
            ("combine_c", 0.147, 0.037, 0.14, 0.133),
            ("combine_d", -0.053, -0.117, 0.127, 0.16),
            ("combine_d", 0.053, -0.117, 0.127, 0.16),
            ("combine_e", -0.033, -0.03, 0.153, 0.16),
            ("combine_e", 0.033, -0.03, 0.153, 0.16),
            ("combine_f", 0.0, 0.003, 0.127, 0.12),
        ),
    ),
    # 4-3: boss candidate #083.
    "locust": final_boss(
        "LOCUST",
        "locust",
        0.7,
        0.387,
        9,
        ("missiles", "pellets", "curve", "spiral"),
        (
            ("locust_a", -0.18, -0.083, 0.153, 0.227),
            ("locust_a", 0.18, -0.083, 0.153, 0.227),
            ("locust_b", -0.207, 0.163, 0.18, 0.26),
            ("locust_b", 0.207, 0.163, 0.18, 0.26),
            ("locust_c", -0.32, 0.05, 0.167, 0.193),
            ("locust_c", 0.32, 0.05, 0.167, 0.193),
            ("locust_d", -0.093, 0.157, 0.153, 0.187),
            ("locust_d", 0.093, 0.157, 0.153, 0.187),
            ("locust_e", -0.027, 0.01, 0.127, 0.153),
            ("locust_e", 0.027, 0.01, 0.127, 0.153),
        ),
    ),
    # 4-4: boss candidate #066.
    "granary": final_boss(
        "GRANARY",
        "granary",
        0.607,
        0.447,
        10,
        ("cluster", "aimed", "laser", "wave"),
        (
            ("granary_a", -0.073, 0.12, 0.113, 0.173),
            ("granary_a", 0.073, 0.12, 0.113, 0.173),
            ("granary_b", -0.18, 0.0, 0.167, 0.167),
            ("granary_b", 0.18, 0.0, 0.167, 0.167),
            ("granary_c", -0.06, -0.167, 0.14, 0.147),
            ("granary_c", 0.06, -0.167, 0.14, 0.147),
            ("granary_d", -0.08, 0.033, 0.113, 0.22),
            ("granary_d", 0.08, 0.033, 0.113, 0.22),
            ("granary_e", -0.08, -0.047, 0.153, 0.22),
            ("granary_e", 0.08, -0.047, 0.153, 0.22),
        ),
    ),
    # 4-5: boss candidate #010.
    "harrowmaster": final_boss(
        "HARROWMASTER",
        "harrowmaster",
        0.647,
        0.427,
        11,
        ("accel", "rockets", "laser", "curve"),
        (
            ("harrowmaster_a", -0.26, 0.103, 0.193, 0.16),
            ("harrowmaster_b", -0.127, 0.13, 0.087, 0.113),
            ("harrowmaster_c", -0.12, -0.023, 0.127, 0.193),
            ("harrowmaster_d", -0.04, -0.15, 0.167, 0.293),
            ("harrowmaster_a", -0.033, -0.05, 0.193, 0.16),
            ("harrowmaster_a", 0.033, -0.05, 0.193, 0.16),
            ("harrowmaster_e", -0.247, 0.197, 0.127, 0.12),
            ("harrowmaster_f", 0.247, 0.197, 0.127, 0.12),
            ("harrowmaster_g", 0.0, 0.063, 0.153, 0.253),
        ),
    ),
    # 4-6: boss candidate #103.
    "black_harvest": final_boss(
        "BLACK HARVEST",
        "black_harvest",
        0.74,
        0.373,
        12,
        ("curve", "missiles", "laser", "accel"),
        (
            ("black_harvest_a", -0.167, -0.063, 0.167, 0.213),
            ("black_harvest_a", 0.167, -0.063, 0.167, 0.213),
            ("black_harvest_b", -0.053, -0.077, 0.26, 0.233),
            ("black_harvest_b", 0.053, -0.077, 0.26, 0.233),
            ("black_harvest_c", -0.207, -0.177, 0.127, 0.187),
            ("black_harvest_c", 0.207, -0.177, 0.127, 0.187),
            ("black_harvest_d", -0.267, -0.057, 0.207, 0.22),
            ("black_harvest_d", 0.267, -0.057, 0.207, 0.22),
            ("black_harvest_e", -0.187, 0.043, 0.167, 0.187),
            ("black_harvest_e", 0.187, 0.043, 0.167, 0.187),
        ),
    ),
    # 5-1: boss candidate #024.
    "maelstrom": final_boss(
        "MAELSTROM",
        "maelstrom",
        0.66,
        0.427,
        9,
        ("wave", "curve", "ring", "laser"),
        (
            ("maelstrom_a", -0.28, 0.103, 0.167, 0.133),
            ("maelstrom_a", 0.28, 0.103, 0.167, 0.133),
            ("maelstrom_b", -0.133, -0.023, 0.153, 0.167),
            ("maelstrom_b", 0.133, -0.023, 0.153, 0.167),
            ("maelstrom_c", -0.14, 0.19, 0.207, 0.247),
            ("maelstrom_c", 0.14, 0.19, 0.207, 0.247),
            ("maelstrom_d", -0.14, -0.163, 0.207, 0.22),
            ("maelstrom_d", 0.14, -0.163, 0.207, 0.22),
            ("maelstrom_e", -0.027, 0.003, 0.153, 0.193),
            ("maelstrom_e", 0.027, 0.003, 0.153, 0.193),
        ),
    ),
    # 5-2: boss candidate #039.
    "man_o_war": final_boss(
        "MAN O' WAR",
        "man_o_war",
        0.633,
        0.447,
        10,
        ("missiles", "wave", "laser", "pellets"),
        (
            ("man_o_war_a", -0.153, -0.013, 0.153, 0.187),
            ("man_o_war_a", 0.153, -0.013, 0.153, 0.187),
            ("man_o_war_b", -0.213, -0.22, 0.153, 0.18),
            ("man_o_war_b", 0.213, -0.22, 0.153, 0.18),
            ("man_o_war_c", -0.147, 0.16, 0.113, 0.133),
            ("man_o_war_c", 0.147, 0.16, 0.113, 0.133),
            ("man_o_war_d", -0.087, -0.107, 0.153, 0.193),
            ("man_o_war_d", 0.087, -0.107, 0.153, 0.193),
        ),
    ),
    # 5-3: boss candidate #003.
    "typhoon": final_boss(
        "TYPHOON",
        "typhoon",
        0.687,
        0.413,
        11,
        ("curve", "accel", "wave", "laser"),
        (
            ("typhoon_a", -0.047, 0.097, 0.207, 0.18),
            ("typhoon_a", 0.047, 0.097, 0.207, 0.18),
            ("typhoon_b", -0.093, -0.177, 0.18, 0.233),
            ("typhoon_b", 0.093, -0.177, 0.18, 0.233),
            ("typhoon_c", -0.233, -0.137, 0.113, 0.213),
            ("typhoon_c", 0.233, -0.137, 0.113, 0.213),
            ("typhoon_d", -0.167, 0.077, 0.153, 0.253),
            ("typhoon_d", 0.167, 0.077, 0.153, 0.253),
        ),
    ),
    # 5-4: boss candidate #096.
    "tsunami": final_boss(
        "TSUNAMI",
        "tsunami",
        0.527,
        0.553,
        12,
        ("wave", "cluster", "laser", "spiral"),
        (
            ("tsunami_a", -0.127, 0.133, 0.18, 0.173),
            ("tsunami_b", -0.22, 0.013, 0.14, 0.133),
            ("tsunami_c", 0.22, 0.013, 0.14, 0.133),
            ("tsunami_d", -0.2, 0.08, 0.1, 0.1),
            ("tsunami_e", -0.027, -0.047, 0.153, 0.133),
            ("tsunami_f", -0.24, -0.067, 0.14, 0.153),
            ("tsunami_g", 0.24, -0.067, 0.14, 0.153),
            ("tsunami_h", -0.207, 0.167, 0.167, 0.213),
        ),
    ),
    # 5-5: boss candidate #058.
    "abyssal": final_boss(
        "ABYSSAL",
        "abyssal",
        0.607,
        0.493,
        13,
        ("sniper", "missiles", "curve", "laser"),
        (
            ("abyssal_a", -0.187, -0.143, 0.167, 0.167),
            ("abyssal_b", 0.187, -0.143, 0.167, 0.167),
            ("abyssal_c", -0.16, 0.123, 0.18, 0.253),
            ("abyssal_d", -0.033, 0.097, 0.14, 0.193),
            ("abyssal_d", 0.033, 0.097, 0.14, 0.193),
            ("abyssal_e", -0.18, -0.023, 0.153, 0.187),
            ("abyssal_e", 0.18, -0.023, 0.153, 0.187),
        ),
    ),
    # 5-6: boss candidate #102.
    "kraken": final_boss(
        "KRAKEN",
        "kraken",
        0.5,
        0.6,
        14,
        ("wave", "rockets", "laser", "curve"),
        (
            ("kraken_a", -0.207, -0.277, 0.127, 0.113),
            ("kraken_b", -0.1, -0.237, 0.087, 0.107),
            ("kraken_c", -0.187, 0.03, 0.1, 0.153),
            ("kraken_d", 0.0, 0.063, 0.153, 0.2),
        ),
    ),
    # 6-1: boss candidate #152.
    "mesa": final_boss(
        "MESA",
        "mesa",
        0.713,
        0.433,
        11,
        ("rockets", "sniper", "laser", "fan"),
        (
            ("mesa_a", -0.22, -0.14, 0.14, 0.227),
            ("mesa_a", 0.22, -0.14, 0.14, 0.227),
            ("mesa_b", -0.287, 0.093, 0.18, 0.313),
            ("mesa_b", 0.287, 0.093, 0.18, 0.313),
            ("mesa_c", -0.18, -0.007, 0.113, 0.233),
            ("mesa_c", 0.18, -0.007, 0.113, 0.233),
            ("mesa_d", -0.16, 0.153, 0.113, 0.207),
            ("mesa_d", 0.16, 0.153, 0.113, 0.207),
            ("mesa_e", -0.307, -0.027, 0.127, 0.18),
            ("mesa_e", 0.307, -0.027, 0.127, 0.18),
        ),
    ),
    # 6-2: boss candidate #191.
    "dust_devil": final_boss(
        "DUST DEVIL",
        "dust_devil",
        0.72,
        0.44,
        12,
        ("curve", "pellets", "spiral", "accel"),
        (
            ("dust_devil_a", -0.143, 0.19, 0.153, 0.167),
            ("dust_devil_a", 0.143, 0.19, 0.153, 0.167),
            ("dust_devil_b", -0.043, -0.197, 0.18, 0.207),
            ("dust_devil_c", -0.29, 0.063, 0.193, 0.233),
            ("dust_devil_d", -0.037, -0.03, 0.127, 0.147),
            ("dust_devil_d", 0.037, -0.03, 0.127, 0.147),
            ("dust_devil_e", -0.17, -0.003, 0.18, 0.213),
            ("dust_devil_f", -0.023, 0.177, 0.18, 0.207),
            ("dust_devil_g", -0.157, -0.183, 0.193, 0.213),
            ("dust_devil_h", -0.283, -0.097, 0.22, 0.253),
            ("dust_devil_i", 0.283, -0.097, 0.22, 0.253),
            ("dust_devil_j", 0.003, 0.037, 0.14, 0.153),
        ),
    ),
    # 6-3: boss candidate #183.
    "landslide": final_boss(
        "LANDSLIDE",
        "landslide",
        0.74,
        0.467,
        13,
        ("cluster", "rockets", "laser", "wave"),
        (
            ("landslide_a", -0.047, 0.03, 0.153, 0.153),
            ("landslide_a", 0.047, 0.03, 0.153, 0.153),
            ("landslide_b", -0.26, 0.103, 0.14, 0.127),
            ("landslide_b", 0.26, 0.103, 0.14, 0.127),
            ("landslide_c", -0.273, 0.01, 0.18, 0.227),
            ("landslide_c", 0.273, 0.01, 0.18, 0.227),
            ("landslide_d", -0.08, -0.203, 0.18, 0.287),
            ("landslide_d", 0.08, -0.203, 0.18, 0.287),
            ("landslide_e", -0.16, -0.103, 0.22, 0.293),
            ("landslide_e", 0.16, -0.103, 0.22, 0.293),
        ),
    ),
    # 6-4: boss candidate #048.
    "basilisk": final_boss(
        "BASILISK",
        "basilisk",
        0.573,
        0.607,
        14,
        ("accel", "sniper", "laser", "curve"),
        (
            ("basilisk_a", -0.223, -0.093, 0.167, 0.24),
            ("basilisk_b", -0.023, -0.067, 0.18, 0.227),
            ("basilisk_c", 0.023, -0.067, 0.18, 0.227),
            ("basilisk_d", -0.143, -0.027, 0.113, 0.167),
            ("basilisk_d", 0.143, -0.027, 0.113, 0.167),
            ("basilisk_e", 0.003, 0.033, 0.167, 0.14),
        ),
    ),
    # 6-5: boss candidate #094.
    "sandworm": final_boss(
        "SANDWORM",
        "sandworm",
        0.607,
        0.573,
        15,
        ("missiles", "wave", "curve", "laser"),
        (
            ("sandworm_a", -0.113, 0.077, 0.207, 0.18),
            ("sandworm_a", 0.113, 0.077, 0.207, 0.18),
            ("sandworm_b", -0.173, 0.203, 0.127, 0.173),
            ("sandworm_b", 0.173, 0.203, 0.127, 0.173),
            ("sandworm_c", -0.06, 0.19, 0.127, 0.16),
            ("sandworm_c", 0.06, 0.19, 0.127, 0.16),
            ("sandworm_d", -0.073, -0.097, 0.193, 0.233),
            ("sandworm_d", 0.073, -0.097, 0.193, 0.233),
            ("sandworm_e", 0.0, -0.097, 0.14, 0.113),
        ),
    ),
    # 6-6: boss candidate #031.
    "monolith": final_boss(
        "MONOLITH",
        "monolith",
        0.553,
        0.633,
        16,
        ("sniper", "cluster", "laser", "accel"),
        (
            ("monolith_a", -0.113, 0.08, 0.14, 0.153),
            ("monolith_a", 0.113, 0.08, 0.14, 0.153),
            ("monolith_b", -0.027, -0.22, 0.127, 0.16),
            ("monolith_b", 0.027, -0.22, 0.127, 0.16),
            ("monolith_c", -0.067, -0.313, 0.1, 0.12),
            ("monolith_c", 0.067, -0.313, 0.1, 0.12),
            ("monolith_d", -0.067, 0.26, 0.18, 0.2),
            ("monolith_d", 0.067, 0.26, 0.18, 0.2),
        ),
    ),
    # 7-1: boss candidate #158.
    "furnace": final_boss(
        "FURNACE",
        "furnace",
        0.733,
        0.48,
        13,
        ("fan", "rockets", "laser", "pellets"),
        (
            ("furnace_a", -0.263, -0.07, 0.193, 0.18),
            ("furnace_b", 0.263, -0.07, 0.193, 0.18),
            ("furnace_c", -0.11, -0.21, 0.127, 0.113),
            ("furnace_d", 0.11, -0.21, 0.127, 0.113),
            ("furnace_e", -0.223, 0.097, 0.193, 0.247),
            ("furnace_f", -0.123, 0.07, 0.26, 0.213),
            ("furnace_g", -0.35, 0.05, 0.18, 0.207),
            ("furnace_h", -0.17, -0.09, 0.193, 0.193),
            ("furnace_i", -0.137, 0.19, 0.26, 0.307),
            ("furnace_i", 0.137, 0.19, 0.26, 0.307),
        ),
    ),
    # 7-2: boss candidate #156.
    "smokestack": final_boss(
        "SMOKESTACK",
        "smokestack",
        0.66,
        0.533,
        14,
        ("cluster", "accel", "curve", "laser"),
        (
            ("smokestack_a", -0.307, 0.21, 0.18, 0.167),
            ("smokestack_a", 0.307, 0.21, 0.18, 0.167),
            ("smokestack_b", -0.033, -0.223, 0.207, 0.253),
            ("smokestack_b", 0.033, -0.223, 0.207, 0.253),
            ("smokestack_c", -0.087, 0.097, 0.127, 0.127),
            ("smokestack_c", 0.087, 0.097, 0.127, 0.127),
            ("smokestack_d", -0.067, 0.197, 0.153, 0.167),
            ("smokestack_d", 0.067, 0.197, 0.153, 0.167),
        ),
    ),
    # 7-3: boss candidate #047.
    "slag_king": final_boss(
        "SLAG KING",
        "slag_king",
        0.593,
        0.6,
        15,
        ("pellets", "missiles", "laser", "wave"),
        (
            ("slag_king_a", -0.173, -0.037, 0.167, 0.18),
            ("slag_king_a", 0.173, -0.037, 0.167, 0.18),
            ("slag_king_b", -0.12, 0.123, 0.113, 0.153),
            ("slag_king_b", 0.12, 0.123, 0.113, 0.153),
            ("slag_king_c", -0.14, -0.123, 0.1, 0.087),
            ("slag_king_c", 0.14, -0.123, 0.1, 0.087),
            ("slag_king_d", -0.093, 0.21, 0.167, 0.2),
            ("slag_king_d", 0.093, 0.21, 0.167, 0.2),
            ("slag_king_e", -0.2, 0.137, 0.14, 0.133),
            ("slag_king_e", 0.2, 0.137, 0.14, 0.133),
        ),
    ),
    # 7-4: boss candidate #084.
    "forgemaster": final_boss(
        "FORGEMASTER",
        "forgemaster",
        0.673,
        0.54,
        16,
        ("rockets", "sniper", "laser", "curve"),
        (
            ("forgemaster_a", -0.18, -0.193, 0.14, 0.167),
            ("forgemaster_a", 0.18, -0.193, 0.14, 0.167),
            ("forgemaster_b", -0.14, 0.053, 0.127, 0.173),
            ("forgemaster_b", 0.14, 0.053, 0.127, 0.173),
            ("forgemaster_c", -0.233, 0.06, 0.153, 0.187),
            ("forgemaster_c", 0.233, 0.06, 0.153, 0.187),
            ("forgemaster_d", -0.047, -0.02, 0.1, 0.133),
            ("forgemaster_d", 0.047, -0.02, 0.1, 0.133),
            ("forgemaster_e", -0.073, -0.16, 0.1, 0.113),
            ("forgemaster_e", 0.073, -0.16, 0.1, 0.113),
        ),
    ),
    # 7-5: boss candidate #043.
    "inferno": final_boss(
        "INFERNO",
        "inferno",
        0.607,
        0.613,
        17,
        ("curve", "cluster", "laser", "accel"),
        (
            ("inferno_a", -0.1, 0.177, 0.153, 0.233),
            ("inferno_a", 0.1, 0.177, 0.153, 0.233),
            ("inferno_b", -0.167, -0.11, 0.153, 0.193),
            ("inferno_b", 0.167, -0.11, 0.153, 0.193),
            ("inferno_c", -0.14, 0.257, 0.153, 0.167),
            ("inferno_c", 0.14, 0.257, 0.153, 0.167),
            ("inferno_d", -0.253, -0.17, 0.113, 0.147),
            ("inferno_d", 0.253, -0.17, 0.113, 0.147),
        ),
    ),
    # 7-6: boss candidate #049.
    "reactor": final_boss(
        "REACTOR",
        "reactor",
        0.647,
        0.593,
        18,
        ("accel", "missiles", "laser", "wave"),
        (
            ("reactor_a", -0.22, -0.007, 0.233, 0.307),
            ("reactor_a", 0.22, -0.007, 0.233, 0.307),
            ("reactor_b", -0.04, -0.213, 0.193, 0.26),
            ("reactor_b", 0.04, -0.213, 0.193, 0.26),
            ("reactor_c", -0.12, 0.253, 0.233, 0.213),
            ("reactor_c", 0.12, 0.253, 0.233, 0.213),
            ("reactor_d", -0.247, -0.127, 0.113, 0.14),
            ("reactor_d", 0.247, -0.127, 0.113, 0.14),
            ("reactor_e", -0.047, 0.093, 0.127, 0.133),
            ("reactor_e", 0.047, 0.093, 0.127, 0.133),
        ),
    ),
    # 8-1: boss candidate #110.
    "neon_tyrant": final_boss(
        "NEON TYRANT",
        "neon_tyrant",
        0.687,
        0.6,
        15,
        ("sniper", "accel", "laser", "curve"),
        (
            ("neon_tyrant_a", -0.087, 0.05, 0.233, 0.34),
            ("neon_tyrant_b", -0.04, -0.277, 0.18, 0.267),
            ("neon_tyrant_c", -0.287, 0.097, 0.193, 0.24),
            ("neon_tyrant_d", 0.287, 0.097, 0.193, 0.24),
        ),
    ),
    # 8-2: boss candidate #186.
    "gridlock": final_boss(
        "GRIDLOCK",
        "gridlock",
        0.673,
        0.613,
        16,
        ("missiles", "pellets", "laser", "wave"),
        (
            ("gridlock_a", -0.267, 0.277, 0.18, 0.233),
            ("gridlock_a", 0.267, 0.277, 0.18, 0.233),
            ("gridlock_b", -0.08, 0.017, 0.14, 0.193),
            ("gridlock_b", 0.08, 0.017, 0.14, 0.193),
            ("gridlock_c", -0.06, 0.15, 0.167, 0.22),
            ("gridlock_c", 0.06, 0.15, 0.167, 0.22),
            ("gridlock_d", -0.173, 0.143, 0.233, 0.26),
            ("gridlock_d", 0.173, 0.143, 0.233, 0.26),
            ("gridlock_e", -0.1, 0.27, 0.193, 0.22),
            ("gridlock_e", 0.1, 0.27, 0.193, 0.22),
            ("gridlock_f", 0.0, 0.043, 0.18, 0.24),
        ),
    ),
    # 8-3: boss candidate #081.
    "blackout": final_boss(
        "BLACKOUT",
        "blackout",
        0.707,
        0.587,
        17,
        ("curve", "rockets", "laser", "accel"),
        (
            ("blackout_a", -0.15, 0.083, 0.18, 0.26),
            ("blackout_a", 0.15, 0.083, 0.18, 0.26),
            ("blackout_b", -0.263, -0.01, 0.167, 0.247),
            ("blackout_c", -0.23, 0.23, 0.127, 0.16),
            ("blackout_d", -0.023, -0.21, 0.14, 0.227),
            ("blackout_d", 0.023, -0.21, 0.14, 0.227),
            ("blackout_e", -0.037, 0.13, 0.193, 0.22),
            ("blackout_e", 0.037, 0.13, 0.193, 0.22),
        ),
    ),
    # 8-4: boss candidate #072.
    "skybreaker": final_boss(
        "SKYBREAKER",
        "skybreaker",
        0.767,
        0.553,
        18,
        ("wave", "sniper", "laser", "cluster"),
        (
            ("skybreaker_a", -0.28, 0.067, 0.22, 0.233),
            ("skybreaker_a", 0.28, 0.067, 0.22, 0.233),
            ("skybreaker_b", -0.18, 0.067, 0.247, 0.293),
            ("skybreaker_b", 0.18, 0.067, 0.247, 0.293),
            ("skybreaker_c", -0.293, -0.127, 0.247, 0.307),
            ("skybreaker_c", 0.293, -0.127, 0.247, 0.307),
            ("skybreaker_d", -0.227, 0.227, 0.14, 0.173),
            ("skybreaker_d", 0.227, 0.227, 0.14, 0.173),
            ("skybreaker_e", -0.153, -0.1, 0.26, 0.207),
            ("skybreaker_e", 0.153, -0.1, 0.26, 0.207),
            ("skybreaker_f", 0.0, 0.013, 0.193, 0.193),
        ),
    ),
    # 8-5: boss candidate #121.
    "sovereign": final_boss(
        "SOVEREIGN",
        "sovereign",
        0.74,
        0.607,
        19,
        ("accel", "missiles", "laser", "curve"),
        (
            ("sovereign_a", -0.187, -0.187, 0.1, 0.147),
            ("sovereign_a", 0.187, -0.187, 0.1, 0.147),
            ("sovereign_b", -0.147, 0.087, 0.233, 0.213),
            ("sovereign_b", 0.147, 0.087, 0.233, 0.213),
            ("sovereign_c", -0.233, -0.067, 0.273, 0.247),
            ("sovereign_c", 0.233, -0.067, 0.273, 0.247),
            ("sovereign_d", -0.287, -0.207, 0.233, 0.22),
            ("sovereign_d", 0.287, -0.207, 0.233, 0.22),
        ),
    ),
    # 8-6: boss candidate #155.
    "singularity": final_boss(
        "SINGULARITY",
        "singularity",
        0.767,
        0.6,
        20,
        ("curve", "cluster", "laser", "spiral"),
        (
            ("singularity_a", -0.073, -0.137, 0.26, 0.273),
            ("singularity_a", 0.073, -0.137, 0.26, 0.273),
            ("singularity_b", -0.027, -0.023, 0.207, 0.2),
            ("singularity_b", 0.027, -0.023, 0.207, 0.2),
            ("singularity_c", -0.193, -0.11, 0.233, 0.227),
            ("singularity_c", 0.193, -0.11, 0.233, 0.227),
            ("singularity_d", 0.0, 0.09, 0.153, 0.167),
        ),
    ),
}
