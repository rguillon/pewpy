"""Writing a batch of background candidates (see the package)."""

import argparse
import json
import random

from pewpy.data import SOURCE_DATA
from pewpy.scenery import params
from pewpy.tools import background_candidates
from pewpy.tools.background_candidates.themes import THEMES, Theme
from pewpy.tools.common import batch
from pewpy.tools.common.geometry import Rng

DEFAULT_OUT = SOURCE_DATA / "models" / "candidates" / "backgrounds"


def candidate(rng: Rng, name: str, theme: Theme, taken: set[str]) -> dict:
    """Make a candidate of a theme: a level's background fields, a name not `taken` yet, and its theme as its note."""
    names = [f"{adjective} {noun}" for adjective in theme.adjectives for noun in theme.nouns]
    free = [title for title in names if title not in taken] or names
    title = rng.choice(free)
    taken.add(title)
    scenery = theme.changes(rng)
    params.resolve(theme.preset, scenery)  # it reads (a SceneryError otherwise)
    low, high = theme.clouds
    return {
        "name": title,
        "note": f"theme: {name}",
        "background": theme.preset,
        "scenery": scenery,
        "time_of_day": rng.choice(theme.times),
        "clouds": round(rng.uniform(low, high), 2),
        "background_seed": rng.randrange(1_000_000),
    }


def main() -> None:
    """Generate the backgrounds the command line asks for and write them: one per theme, shuffled, none twice."""
    parser = argparse.ArgumentParser(
        description=background_candidates.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--count", type=int, default=len(THEMES), help=f"how many themes to show, one each (default all {len(THEMES)})"
    )
    batch.options(parser, DEFAULT_OUT, "the game's background candidates")
    args = parser.parse_args()
    seed, first = batch.start(args)
    rng = random.Random(seed)
    order = list(THEMES)
    rng.shuffle(order)
    order = order[: max(0, args.count)]  # one candidate per theme: at most as many as there are themes
    taken: set[str] = set()
    for index, name in enumerate(order):
        made = candidate(rng, name, THEMES[name], taken)
        (args.out / f"{first + index:03d}.json").write_text(json.dumps(made, indent=2) + "\n")
    batch.report("background candidates", len(order), first, args.out, seed)


if __name__ == "__main__":
    main()
