"""The waves of a half level: a warm-up, the main waves, a finale of signature enemies."""

import random
from typing import Any

from pewpewdev.tools.levels.difficulty import GROWTH, MAX_DIFFICULTY, between, budget
from pewpewdev.tools.levels.enemies import SHAPES, UNLOCK, WARM_UP
from pewpy.game.enemies.roster import ENEMY_TYPES

KINDS = (6, 17)  # how many kinds of enemies a level sends
FIRST_WAVE = 2.0  # seconds into the level
HALF_TIME = 46.0  # seconds from a half's first wave to its last (then comes its boss)
SECOND_HALF_HARDER = 2  # the second half is as hard as a level this much harder (bigger groups, more of them)
AFTER_MINI_BOSS = 3.0  # seconds from the mini boss's arrival on the waves' clock (it stops while a boss is fought)
TWIN_WAVES = (0.15, 0.35)  # the share of waves sent together with the one before
MIN_GAP = 0.8  # seconds between waves, at least
FINALE_SHARE = 0.2  # the last part of the threat: the signature enemies...
FINALE_PACE = 0.6  # ...closer together
BOSS_DELAY = 6.0  # seconds after a half's last wave
LINE_SPAN = 2.1  # a line of enemies across the screen is at most this wide (the play area is 2.5)
SIDE_SPAN = 1.0  # ...and a line coming in from a side at most this tall


def make_wave(rng: random.Random, enemy: str, d: int) -> dict[str, Any]:
    """Make a group of `enemy` (no time yet), its shape drawn from the enemy's, its size grown to difficulty `d`."""
    shape = dict(rng.choice(SHAPES[enemy]))
    count = max(1, round(shape.pop("count") * GROWTH ** (d - 1)))
    if shape.get("formation") == "line" and count > 1:
        span = SIDE_SPAN if "side" in shape else LINE_SPAN
        count = min(count, int(span / shape.get("spacing", 0.2)) + 1)
    wave: dict[str, Any] = {"enemy": enemy}
    if count > 1 or "formation" in shape:
        wave["count"] = count
    return {**wave, **shape}


def threat(wave: dict[str, Any]) -> int:
    """Return what a wave is worth: the points of its enemies (the tougher an enemy, the more points)."""
    return wave.get("count", 1) * ENEMY_TYPES[wave["enemy"]].points


def make_half(rng: random.Random, pool: list[str], d: int, start: float, harder: int = 0) -> list[dict[str, Any]]:
    """Make a half level's waves from `start`, of the enemies of `pool`, for a level of difficulty `d`.

    Its groups' size and threat are those of a level `harder` steps harder: a warm-up wave, the main waves, then a
    finale of its signature enemies (the newest first) close together; the last at `start` + HALF_TIME.
    """
    newest = [enemy for enemy in pool if UNLOCK[enemy] == d]
    older = [enemy for enemy in pool if enemy not in newest]
    signature = (newest + rng.sample(older, len(older)))[: rng.randint(2, 3)]
    weights = [1 + UNLOCK[enemy] for enemy in pool]  # the newer enemies more often
    main = list(signature)
    while len(main) < min(round(between(KINDS, d)), len(pool)):
        enemy = rng.choices(pool, weights)[0]
        if enemy not in main:
            main.append(enemy)
    # The waves, until their threat reaches the half's; the last ones (the finale) of the signature enemies.
    size = d + harder
    goal = budget(size)
    groups = [make_wave(rng, rng.choice([e for e in WARM_UP if e in pool]), size)]
    while sum(map(threat, groups)) < goal:
        finale = sum(map(threat, groups)) > goal * (1 - FINALE_SHARE)
        groups.append(make_wave(rng, rng.choice(signature if finale else main), size))
    # Spread over the half: each wave gets time in proportion to its threat; sometimes two come together.
    total = sum(map(threat, groups))
    finale_from = next(
        i for i, _ in enumerate(groups) if sum(map(threat, groups[: i + 1])) > total * (1 - FINALE_SHARE)
    )
    twins = between(TWIN_WAVES, min(size, MAX_DIFFICULTY))
    time, waves = 0.0, []
    for i, group in enumerate(groups):
        if i > 0 and not (rng.random() < twins and waves[-1]["time"] == time):
            share = HALF_TIME * threat(groups[i - 1]) / total
            time += max(MIN_GAP, share * (FINALE_PACE if i > finale_from else rng.uniform(0.8, 1.2)))
        waves.append({"time": time, **group})
    stretch = HALF_TIME / max(time, 1.0)  # the last wave at HALF_TIME
    for wave in waves:
        wave["time"] = round(start + wave["time"] * stretch, 1)
    return waves
