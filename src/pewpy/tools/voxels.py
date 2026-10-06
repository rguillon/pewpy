"""Move a model between the game's forms: a flat drawing, a 3D (layered) drawing, a MagicaVoxel model.

    make voxels ARGS="export drone"     # models/enemies/drone.vox: open it in MagicaVoxel (the game doesn't use it yet)
    make voxels ARGS="use drone"        # the game now draws models/enemies/drone.vox (drone.json keeps its engines)
    make voxels ARGS="layers drone"     # drone.json becomes a 3D drawing: its layers, to edit as text

(or `uv run python -m pewpy.tools.voxels ...`). NAME is a model's file name without ".json", like "drone" (found in
its group, see pewpy.data.model_path), or "candidates/enemies/007". In MagicaVoxel the ship lies on the ground seen from
above like in the game: its nose where it points on screen, z up towards the camera. Engines stay in the .json file ("x"
and "y" on the drawing, "z" cubes above its middle plane), and so does a finer model's "scale"; "use" and "layers" keep
them. `git checkout` a model's .json to go back.
"""

import argparse
import json
from pathlib import Path

from pewpy.graphics import models
from pewpy.graphics.models.drawings import vox
from pewpy.tools.models.registry import model_file
from pewpy.tools.paths import REPOSITORY


class NotExportedError(SystemExit):
    """A model has no .vox file to use."""

    def __init__(self, name: str) -> None:
        super().__init__(f"no {name}.vox: export it first")


def export(name: str) -> Path:
    """Export the model as a .vox file next to its .json (it stays as it is)."""
    path = model_file(name, ".vox")
    path.write_bytes(vox.write(models.voxels_to_vox(models.load_voxels(name))))
    return path


def use(name: str) -> Path:
    """Make the model's .json name its .vox file (exported before, then edited), keeping its engines."""
    path = model_file(name)
    if not model_file(name, ".vox").is_file():
        raise NotExportedError(name)
    data = json.loads(path.read_text())
    data = {"vox": f"{Path(name).name}.vox", **_kept(data)}
    path.write_text(json.dumps(data, indent=2) + "\n")
    models.load_voxels(name)  # it reads
    return path


def layers(name: str) -> Path:
    """Rewrite the model's .json as a 3D drawing: slices from the top (nearest the camera) down, keeping its engines."""
    path = model_file(name)
    data = json.loads(path.read_text())
    voxels = models.load_voxels(name)
    chars: dict[tuple[float, ...], str] = {}
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@$%&*+=?!"
    for color in voxels.cells.values():
        if color not in chars:
            chars[color] = letters[len(chars)]
    # Slices from -extent to +extent: read back, the middle one lands on the middle plane, so every cube is where
    # it was (and the engines' "z" still fits).
    extent = max(abs(layer) for _, _, layer in voxels.cells)
    slices = [
        [
            "".join(
                chars[voxels.cells[column, row, layer]] if (column, row, layer) in voxels.cells else "."
                for column in range(voxels.width)
            )
            for row in range(voxels.height)
        ]
        for layer in range(-extent, extent + 1)
    ]
    palette = {char: {"color": [round(value, 3) for value in color[:3]]} for color, char in chars.items()}
    scale = {"scale": voxels.scale} if voxels.scale != 1 else {}
    result = {**scale, "layers": slices, "palette": palette, **_kept(data, scale=False)}
    path.write_text(json.dumps(result, indent=2) + "\n")
    return path


def _kept(data: dict, scale: bool = True) -> dict:
    """Return what a model file keeps whatever its form: its engines, and its scale (finer models)."""
    keys = ("scale", "engines") if scale else ("engines",)
    return {key: data[key] for key in keys if key in data}


def main() -> None:
    """Run the command on every model named."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("export", "use", "layers"))
    parser.add_argument("names", nargs="+", help="models, like drone or candidates/007")
    args = parser.parse_args()
    action = {"export": export, "use": use, "layers": layers}[args.command]
    for name in args.names:
        print(f"{args.command} {name}: {action(name).relative_to(REPOSITORY)}")


if __name__ == "__main__":
    main()
