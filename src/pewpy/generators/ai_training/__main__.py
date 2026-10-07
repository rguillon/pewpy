"""The AI's training from the command line (`make learn`, `make winrate`).

python -m pewpy.generators.ai_training learn [--generations 100] [--ships vanguard ...] [--levels 1-1 ... | all] [--new]
    [--workers 7] [--folder ...]
python -m pewpy.generators.ai_training winrate [--runs 10] [--lives 1] [--ships ...]
"""

import argparse
import time
from pathlib import Path

import numpy as np

from pewpy.ai import files
from pewpy.ai.brain import Brain
from pewpy.ai.files import BRAIN_FOLDER
from pewpy.data import SOURCE_DATA
from pewpy.game.player import REGULAR_SHIPS, SHIPS
from pewpy.generators.ai_training.learning import Report, every_level, learn, level_index
from pewpy.generators.ai_training.winrate import RUNS, win_rates


def main() -> None:
    """Learn or measure the win rates, as the command line says, printing the progress."""
    parser = argparse.ArgumentParser(prog="python -m pewpy.generators.ai_training", description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["learn", "winrate"])
    parser.add_argument("--ships", nargs="+", choices=list(REGULAR_SHIPS), default=list(REGULAR_SHIPS))
    parser.add_argument("--generations", type=int, default=100, help="learn: more generations (100)")
    parser.add_argument(
        "--levels", nargs="+", help='learn: only on these levels ("1-1 2-3"), or on every level ("all"), no curriculum'
    )
    parser.add_argument("--new", action="store_true", help="learn: start a new brain (replacing the saved one)")
    parser.add_argument("--runs", type=int, default=RUNS, help=f"winrate: runs per level and ship ({RUNS})")
    parser.add_argument("--lives", type=int, default=1, help="winrate: lives per run (1, as in training)")
    parser.add_argument("--workers", type=int, help="processes playing in parallel (default: the cores but one)")
    parser.add_argument(
        "--folder", type=Path, default=SOURCE_DATA / BRAIN_FOLDER, help="where the brain is (default: data/brain/)"
    )
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
        winrate(args)
    print(f"{time.monotonic() - start:.0f} s")


def winrate(args: argparse.Namespace) -> None:
    """Play every level with the saved brain (a new one without), printing each level's win rates, then the totals."""
    training = files.load_training(args.folder)
    brain = training.brain if training else Brain.random(np.random.default_rng(0))
    print(f"brain: {f'generation {training.generation}' if training else 'none saved, a new one'}")
    lives = f"{args.lives} li{'ves' if args.lives > 1 else 'fe'}"
    print(f"{args.runs} runs per level and ship, {lives} each: the share of runs that clear the level\n")
    names = "".join(f"{SHIPS[ship].name[:10]:>11}" for ship in args.ships)
    print(f"{'LEVEL':<24}{names}{'ALL':>8}")

    def show(place: str, name: str, rates: dict[str, float]) -> None:
        cells = "".join(f"{100 * rates[ship]:10.0f}%" for ship in args.ships)
        print(f"{place:<4} {name:<19}{cells}{100 * np.mean(list(rates.values())):7.0f}%")

    rates = win_rates(brain, args.ships, args.runs, args.lives, args.workers, show)
    print()
    worlds = sorted({place.split("-")[0] for place in rates}, key=int)
    for world in [*worlds, None]:
        levels = [r for place, r in rates.items() if world is None or place.split("-")[0] == world]
        cells = "".join(f"{100 * np.mean([r[ship] for r in levels]):10.0f}%" for ship in args.ships)
        overall = 100 * np.mean([value for r in levels for value in r.values()])
        print(f"{f'world {world}' if world else 'every level':<24}{cells}{overall:7.0f}%")


if __name__ == "__main__":
    main()
