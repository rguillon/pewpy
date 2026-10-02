"""Writing a batch of boss candidates (see the package)."""

import argparse
import time
from pathlib import Path

from pewpewdev.paths import DATA
from pewpewdev.tools.boss_candidates.selection import generate
from pewpewdev.yamlfiles import dump_yaml

DEFAULT_OUT = DATA / "models" / "boss_candidates"


def write(out: Path, number: int, candidate: dict) -> None:
    """Write a candidate: its core's drawing, its parts' drawings (each once) and where the parts go."""
    name = f"{number:03d}"
    (out / f"{name}.yaml").write_text(dump_yaml(candidate["core"]))
    drawings: dict[str, str] = {}  # the same part drawing placed twice is written once
    layout = []
    for part_drawing, x, y in candidate["parts"]:
        text = dump_yaml(part_drawing)
        if text not in drawings:
            drawings[text] = f"{name}_{chr(ord('a') + len(drawings))}"
            (out / f"{drawings[text]}.yaml").write_text(text)
        layout.append({"drawing": drawings[text], "x": round(x, 2), "y": round(y, 2)})
    (out / f"{name}.parts.yaml").write_text(dump_yaml({"parts": layout}))


def main() -> None:
    """Generate the bosses the command line asks for and write them."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=200, help="how many bosses to write (default 40)")
    parser.add_argument("--seed", type=int, help="the same seed makes the same batch (default: a new one)")
    parser.add_argument("--pool", type=int, default=6, help="how many generated for each one kept (default 6)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="where (default: the game's boss candidates)")
    parser.add_argument("--append", action="store_true", help="number after the ones there instead of replacing them")
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else int(time.time() * 1000) % 1_000_000
    args.out.mkdir(parents=True, exist_ok=True)
    existing = sorted(args.out.glob("*.yaml"))
    first = 1
    if args.append:
        first = max((int(path.name.split(".")[0].split("_")[0]) for path in existing), default=0) + 1
    else:
        for path in existing:
            path.unlink()
    for number, candidate in enumerate(generate(args.count, seed, args.pool), start=first):
        write(args.out, number, candidate)
    print(f"wrote {args.count} boss candidates ({first:03d} to {first + args.count - 1:03d}) to {args.out}")
    print(f"seed {seed}: --seed {seed} makes the same batch again")


if __name__ == "__main__":
    main()
