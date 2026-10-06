"""Writing a batch of candidates (see the package)."""

import argparse
import json

from pewpy.data import SOURCE_DATA
from pewpy.tools.candidates.selection import MIXES, generate
from pewpy.tools.common import batch

DEFAULT_OUT = SOURCE_DATA / "models" / "candidates" / "enemies"


def main() -> None:
    """Generate the candidates the command line asks for and write them."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=500, help="how many to write (default 500)")
    parser.add_argument(
        "--kind",
        choices=MIXES,
        default="all",
        help="one kind (fighter, interceptor, bomber, drone, gunship, heavy) or all",
    )
    parser.add_argument("--pool", type=int, default=7, help="how many generated for each one kept (default 7)")
    batch.options(parser, DEFAULT_OUT, "the game's candidates")
    args = parser.parse_args()
    seed, first = batch.start(args)
    for number, drawing in enumerate(generate(args.count, args.kind, seed, args.pool), start=first):
        (args.out / f"{number:03d}.json").write_text(json.dumps(drawing, indent=2) + "\n")
    batch.report(f"{args.kind} candidates", args.count, first, args.out, seed)


if __name__ == "__main__":
    main()
