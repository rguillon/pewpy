"""Writing a batch of player ship candidates (see the package)."""

import argparse
import json

from pewpy.data import SOURCE_DATA
from pewpy.tools import player_candidates
from pewpy.tools.candidates.selection import PLAYER_MIXES, generate
from pewpy.tools.common import batch

DEFAULT_OUT = SOURCE_DATA / "models" / "candidates" / "player"


def main() -> None:
    """Generate the player ship candidates the command line asks for and write them."""
    parser = argparse.ArgumentParser(
        description=player_candidates.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--count", type=int, default=60, help="how many to write (default 60)")
    parser.add_argument("--kind", choices=PLAYER_MIXES, default="all", help="vanguard, juggernaut, phantom or all")
    parser.add_argument("--pool", type=int, default=7, help="how many generated for each one kept (default 7)")
    batch.options(parser, DEFAULT_OUT, "the game's player candidates")
    args = parser.parse_args()
    seed, first = batch.start(args)
    ships = generate(args.count, args.kind, seed, args.pool, player=True)
    for number, drawing in enumerate(ships, start=first):
        (args.out / f"{number:03d}.json").write_text(json.dumps(drawing, indent=2) + "\n")
    batch.report(f"{args.kind} player candidates", args.count, first, args.out, seed)


if __name__ == "__main__":
    main()
