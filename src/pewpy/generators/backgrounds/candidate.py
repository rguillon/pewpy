"""A background candidate, made from its theme and seed (see the package)."""

import random
from typing import Any

from pewpy.generators.backgrounds.themes import THEMES
from pewpy.scenery import params


def candidate(theme: str, seed: int) -> dict[str, Any]:
    """Make a candidate of a theme: a level's background fields, a name from the theme's words, the theme as its note.

    The same theme and seed make the same candidate; its scenery is checked (a SceneryError otherwise).
    """
    rng = random.Random(seed)
    made = THEMES[theme]
    title = rng.choice([f"{adjective} {noun}" for adjective in made.adjectives for noun in made.nouns])
    scenery = made.changes(rng)
    params.resolve(made.preset, scenery)  # it reads
    low, high = made.clouds
    return {
        "name": title,
        "note": f"theme: {theme}",
        "background": made.preset,
        "scenery": scenery,
        "time_of_day": rng.choice(made.times),
        "clouds": round(rng.uniform(low, high), 2),
        "background_seed": rng.randrange(1_000_000),
    }
