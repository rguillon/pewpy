"""The command line of a batch of candidates: its seed, where it goes, replacing the batch there or adding to it.

parser = argparse.ArgumentParser(...)
batch_options(parser, DEFAULT_OUT, "the game's boss candidates")
args = parser.parse_args()
seed, first = start(args)
... write the candidates, numbered from `first` (001.json, 002.json...; a candidate's other files start with its
number: 007_a.json, 007.parts.json) ...
report("boss candidates", count, first, args.out, seed)
"""

import argparse
import time
from pathlib import Path


def options(parser: argparse.ArgumentParser, out: Path, where: str) -> None:
    """Add the options of a batch: --seed, --out (`out` by default, described as `where`) and --append."""
    parser.add_argument("--seed", type=int, help="the same seed makes the same batch (default: a new one)")
    parser.add_argument("--out", type=Path, default=out, help=f"where (default: {where})")
    parser.add_argument("--append", action="store_true", help="number after the ones there instead of replacing them")


def start(args: argparse.Namespace) -> tuple[int, int]:
    """Get the batch's folder ready (emptied of its JSON files, unless appending); return its seed and first number."""
    seed = args.seed if args.seed is not None else int(time.time() * 1000) % 1_000_000
    args.out.mkdir(parents=True, exist_ok=True)
    existing = sorted(args.out.glob("*.json"))
    if args.append:
        numbers = (path.name.split(".")[0].split("_")[0] for path in existing)
        return seed, max((int(number) for number in numbers if number.isdigit()), default=0) + 1
    for path in existing:
        path.unlink()
    return seed, 1


def report(what: str, count: int, first: int, out: Path, seed: int) -> None:
    """Say what was written, and how to make the same batch again."""
    print(f"wrote {count} {what} ({first:03d} to {first + count - 1:03d}) to {out}")
    print(f"seed {seed}: --seed {seed} makes the same batch again")
