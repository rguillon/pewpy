"""The AI from the command line (`make learn`, `make rate`):

python -m pewpy.ai learn [--generations 100] [--ships vanguard ...] [--workers 7] [--folder ...]
python -m pewpy.ai rate [--runs 10] [--ships ...]
"""

import argparse
import time
from pathlib import Path

from pewpy.ai import files
from pewpy.ai.learning import learn
from pewpy.ai.rating import RUNS, Rating, rate
from pewpy.game.player import SHIPS


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m pewpy.ai", description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["learn", "rate"])
    parser.add_argument("--ships", nargs="+", choices=list(SHIPS), default=list(SHIPS))
    parser.add_argument("--generations", type=int, default=100, help="learn: more generations per ship (100)")
    parser.add_argument("--runs", type=int, default=RUNS, help=f"rate: runs per level ({RUNS})")
    parser.add_argument("--workers", type=int, help="processes playing in parallel (default: the cores but one)")
    parser.add_argument("--folder", type=Path, default=files.ai_folder(), help="where the brains and ratings are")
    args = parser.parse_args()
    start = time.monotonic()
    if args.mode == "learn":

        def report(step) -> None:
            cleared = (
                f"  clears {100 * step.cleared:.0f}% of the levels, gets {100 * (step.progress or 0):.0f}% of the way"
                f"  (trains on {step.worlds} world{'s' if step.worlds > 1 else ''})"
                if step.cleared is not None
                else ""
            )
            print(
                f"{step.ship:10} generation {step.generation:4}  best {step.best:7.1f}  mean {step.mean:7.1f}{cleared}"
            )

        learn(args.ships, args.generations, args.folder, args.workers, report)
    else:

        def show(ship: str, rating: Rating) -> None:
            print(f"{ship:10} {rating.place:4} {rating.name:18} clear rate {rating.clear_rate:5.1f}%")

        rate(args.ships, args.folder, args.runs, args.workers, show)
        print(f"ratings written to {args.folder / 'ratings.json'}")
    print(f"{time.monotonic() - start:.0f} s")


if __name__ == "__main__":
    main()
