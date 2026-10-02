"""Writing a batch of candidates (see the package)."""

import argparse
import json
import time
from pathlib import Path

from pewpewdev.paths import DATA
from pewpewdev.tools.candidates.selection import MIXES, generate

DEFAULT_OUT = DATA / "models" / "candidates"


def main() -> None:
    """Generate the candidates the command line asks for and write them."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=500, help="how many to write (default 200)")
    parser.add_argument("--kind", choices=MIXES, default="all", help="aircraft, industrial or all (default)")
    parser.add_argument("--seed", type=int, help="the same seed makes the same batch (default: a new one)")
    parser.add_argument("--pool", type=int, default=7, help="how many generated for each one kept (default 7)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="where (default: the game's candidates)")
    parser.add_argument("--append", action="store_true", help="number after the ones there instead of replacing them")
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else int(time.time() * 1000) % 1_000_000
    args.out.mkdir(parents=True, exist_ok=True)
    existing = sorted(args.out.glob("*.json"))
    first = 1
    if args.append:
        first = max((int(path.stem) for path in existing if path.stem.isdigit()), default=0) + 1
    else:
        for path in existing:
            path.unlink()
    for number, drawing in enumerate(generate(args.count, args.kind, seed, args.pool), start=first):
        (args.out / f"{number:03d}.json").write_text(json.dumps(drawing, indent=2) + "\n")
    print(f"wrote {args.count} {args.kind} candidates ({first:03d} to {first + args.count - 1:03d}) to {args.out}")
    print(f"seed {seed}: --seed {seed} makes the same batch again")


if __name__ == "__main__":
    main()
