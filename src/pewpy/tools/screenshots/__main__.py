"""Taking the screenshots (see the package)."""

import argparse
from pathlib import Path

from pewpy.data import SOURCE_DATA
from pewpy.tools import screenshots
from pewpy.tools.screenshots import SHOTS, ScreenshotApp

SCREENSHOTS = SOURCE_DATA.parent / "docs" / "screenshots"


def main() -> None:
    """Play every level a moment and save a screenshot of it."""
    parser = argparse.ArgumentParser(
        description=screenshots.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", type=Path, default=SCREENSHOTS, help="where (default: docs/screenshots/)")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    app = ScreenshotApp()
    for world, shot in enumerate(SHOTS):
        path = args.out / f"world_{world + 1}.png"
        app.shoot(world, shot, path)
        print(path)
    app.destroy()
    print(f"{len(SHOTS)} screenshots in {args.out}")


if __name__ == "__main__":
    main()
