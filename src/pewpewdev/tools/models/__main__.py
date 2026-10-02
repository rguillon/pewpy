"""Running the recipes (see the package)."""

import argparse

from pewpewdev.tools import models
from pewpewdev.tools.models.recipes import RECIPES
from pewpewdev.tools.models.registry import MODELS


def main() -> None:
    """Remodel the ships the command line names (all with a recipe by default)."""
    parser = argparse.ArgumentParser(description=models.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="*", help="models to remodel (default: all with a recipe)")
    args = parser.parse_args()
    for name in args.names or RECIPES:
        model, engines = RECIPES[name]()
        model.save(MODELS / f"{name}.json", engines)
        print(f"{name}: {len(model.cells)} cubes")


if __name__ == "__main__":
    main()
