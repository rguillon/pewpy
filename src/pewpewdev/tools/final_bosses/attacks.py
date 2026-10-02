"""The attacks a final boss can have: each one's gun, harder with the difficulty."""

from pewpy.game.weapons.guns import Gun


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
