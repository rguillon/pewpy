"""The AI from the command line (`make learn`, `make rate`).

python -m pewpy.tools.ai learn [--generations 100] [--ships vanguard ...] [--levels 1-1 ... | all] [--new] [--workers 7]
    [--folder ...]
python -m pewpy.tools.ai rate [--runs 10] [--ships ...]
"""

import argparse
import time
from pathlib import Path

from pewpy.game.player import SHIPS
from pewpy.tools.ai import files
from pewpy.tools.ai.learning import Report, every_level, learn, level_index
from pewpy.tools.ai.rating import RUNS, Rating, rate


def main() -> None:
    """Learn or rate, as the command line says, printing the progress."""
    parser = argparse.ArgumentParser(prog="python -m pewpy.tools.ai", description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["learn", "rate"])
    parser.add_argument("--ships", nargs="+", choices=list(SHIPS), default=list(SHIPS))
    parser.add_argument("--generations", type=int, default=100, help="learn: more generations (100)")
    parser.add_argument(
        "--levels", nargs="+", help='learn: only on these levels ("1-1 2-3"), or on every level ("all"), no curriculum'
    )
    parser.add_argument("--new", action="store_true", help="learn: start a new brain (replacing the saved one)")
    parser.add_argument("--runs", type=int, default=RUNS, help=f"rate: runs per level ({RUNS})")
    parser.add_argument("--workers", type=int, help="processes playing in parallel (default: the cores but one)")
    parser.add_argument("--folder", type=Path, default=files.ai_folder(), help="where the brains and ratings are")
    args = parser.parse_args()
    start = time.monotonic()
    if args.mode == "learn":

        def report(step: Report) -> None:
            print(f"generation {step.generation:4}  best {step.best:7.1f}  mean {step.mean:7.1f}")
            if step.checks is not None:
                runs = "runs" if step.levels else "levels"
                for ship, (cleared, progress) in step.checks.items():
                    clears = f"clears {100 * cleared:3.0f}% of the {runs}"
                    print(f"  {ship:10} {clears}, gets {100 * progress:3.0f}% of the way")
                if step.levels:
                    print(f"  (trains on {step.levels} level{'s' if step.levels > 1 else ''})")
                else:
                    print(f"  (trains on {step.worlds} world{'s' if step.worlds > 1 else ''})")

        levels = None
        if args.levels:
            try:
                levels = every_level() if args.levels == ["all"] else tuple(map(level_index, args.levels))
            except ValueError as error:
                parser.error(str(error))
        learn(args.ships, args.generations, args.folder, args.workers, report, levels=levels, new=args.new)
    else:

        def show(ship: str, rating: Rating) -> None:
            print(f"{ship:10} {rating.place:4} {rating.name:18} clear rate {rating.clear_rate:5.1f}%")

        rate(args.ships, args.folder, args.runs, args.workers, show)
        print(f"ratings written to {args.folder / 'ratings.json'}")
    print(f"{time.monotonic() - start:.0f} s")


if __name__ == "__main__":
    main()
