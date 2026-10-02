"""Writing the levels (see the package)."""

import argparse
from pathlib import Path
from typing import Any

from pewpewdev.paths import DATA
from pewpewdev.tools import levels
from pewpewdev.tools.levels.generate import generate
from pewpewdev.tools.levels.worlds import WORLDS
from pewpewdev.yamlfiles import dump_yaml

LEVELS = DATA / "levels"
DEFAULT_SEED = 2024


def write(folder: Path, levels: dict[tuple[int, int], dict[str, Any]]) -> None:
    """Replace every world folder with the generated ones (the background presets, sceneries.yaml, stay)."""
    for old in folder.glob("world_*"):
        for path in old.glob("*.yaml"):
            path.unlink()
        old.rmdir()
    for w, world in enumerate(WORLDS, start=1):
        world_folder = folder / f"world_{w}"
        world_folder.mkdir()
        (world_folder / "world.yaml").write_text(dump_yaml({"name": world.name}))
    for (w, n), level in levels.items():
        (folder / f"world_{w}" / f"level_{n}.yaml").write_text(dump_yaml(level))


def main() -> None:
    """Generate the levels and write them."""
    parser = argparse.ArgumentParser(description=levels.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"the waves' draw (default {DEFAULT_SEED})")
    parser.add_argument("--out", type=Path, default=LEVELS, help="where (default: the game's levels)")
    args = parser.parse_args()
    write(args.out, generate(args.seed))
    print(f"{sum(len(world.levels) for world in WORLDS)} levels in {len(WORLDS)} worlds written to {args.out}")


if __name__ == "__main__":
    main()
