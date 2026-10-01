"""A small kit for modeling ships in real 3D voxels, written out as the game's 3D drawings ("layers").

Recipes are written in the units of the ship's footprint ("units": the cubes of config.MODEL_VOXEL, the same on
every ship): x across (0 at the left edge), y down the drawing (0 at its top: the player's nose, an enemy's tail), z
up towards the camera (0 on the model's middle plane). A model is drawn `scale` cubes per unit: shapes are tested at
every cube's middle, so the same recipe makes a finer model at a bigger scale. Unit cube (x, y, z) spans x to x + 1,
y to y + 1 and z - 0.5 to z + 0.5.

Shapes (most of them mirrored across the middle by default: ships are symmetric): boxes, hull sections lofted along
y with chamfered edges, nacelles (octagonal, along y), plates (wings, fins), and paint. Then `finish` adds the
details: panel seams recessed into the top surfaces, lighter top edges, darker undersides.

Colors are named materials (see MATERIALS); a recipe can add its own (a paint color).
"""

import json
import math
import string
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

Color = tuple[float, float, float]
Cell = tuple[int, int, int]
Inside = Callable[[float, float, float], bool]  # (x, y, z) in units -> inside the shape?

# The industrial look (see decisions.md, "Industrial sci-fi ships"): greys a little dark, teal glass, orange lights.
MATERIALS: dict[str, Color] = {
    "hull": (0.42, 0.43, 0.46),  # the main plating
    "hull_light": (0.55, 0.56, 0.59),  # spines, top edges
    "hull_dark": (0.3, 0.31, 0.34),  # sides, lower plating
    "frame": (0.22, 0.23, 0.25),  # nacelles, structure
    "seam": (0.16, 0.17, 0.19),  # recessed panel lines
    "vent": (0.09, 0.09, 0.1),  # grilles, intakes, nozzles
    "glass": (0.06, 0.16, 0.22),  # cockpit glass...
    "glint": (0.45, 0.78, 0.92),  # ...and its highlight
    "light": (1.0, 0.55, 0.15),  # running lights
    "metal": (0.62, 0.63, 0.66),  # bright metal: barrels, trims
}
PLATING = frozenset({"hull", "hull_light", "hull_dark"})


@dataclass
class Model:
    width: int  # the footprint, in units
    height: int
    scale: int = 1  # cubes per unit
    materials: dict[str, Color] = field(default_factory=lambda: dict(MATERIALS))
    cells: dict[Cell, str] = field(default_factory=dict)

    # -- filling shapes

    def fill(
        self,
        inside: Inside,
        bounds: tuple[float, float, float, float, float, float],
        material: str,
        mirror: bool = True,
        only: Callable[[str | None], bool] | None = None,
    ) -> None:
        """Every cube whose middle is `inside`, within `bounds` (x0, x1, y0, y1, z0, z1 in units), and its mirror
        image. `only`: which cubes it may replace (by their material, None where empty).
        """
        if material not in self.materials:
            raise KeyError(material)
        s = self.scale
        x0, x1, y0, y1, z0, z1 = bounds
        for i in range(max(0, math.floor(x0 * s)), min(self.width * s, math.ceil(x1 * s))):
            x = (i + 0.5) / s
            for j in range(max(0, math.floor(y0 * s)), min(self.height * s, math.ceil(y1 * s))):
                y = (j + 0.5) / s
                for k in range(math.floor(z0 * s) - 1, math.ceil(z1 * s) + 2):
                    if not inside(x, y, k / s + 1e-6):  # just above a layer's middle: whole units fill whole layers
                        continue
                    for cell in {(i, j, k), (self.width * s - 1 - i, j, k)} if mirror else {(i, j, k)}:
                        if only is None or only(self.cells.get(cell)):
                            self.cells[cell] = material

    def box(
        self,
        x: tuple[float, float],
        y: tuple[float, float],
        z: tuple[float, float],
        material: str,
        mirror: bool = True,
    ) -> None:
        """Unit cubes x[0] to x[1], y[0] to y[1], z[0] to z[1] (inclusive)."""
        bounds = (x[0], x[1] + 1, y[0], y[1] + 1, z[0] - 0.5, z[1] + 0.5)

        def inside(px: float, py: float, pz: float) -> bool:
            return bounds[0] <= px <= bounds[1] and bounds[2] <= py <= bounds[3] and bounds[4] <= pz <= bounds[5]

        self.fill(inside, bounds, material, mirror)

    def loft(
        self,
        y: tuple[float, float],
        section: Callable[[float], tuple[float, float, float, float]],
        material: str,
        center: float | None = None,
        mirror: bool = True,
    ) -> None:
        """A hull along y (from y[0] to y[1], in units), around x = `center` (default: the middle): at each point,
        `section(t)` (t from 0 to 1 along it) gives (half width, top, bottom, chamfer), an octagon-like cross-section
        with its corners cut by `chamfer`.
        """
        middle = self.width / 2 if center is None else center
        y0, y1 = y

        def inside(px: float, py: float, pz: float) -> bool:
            if not y0 <= py <= y1:
                return False
            half, top, bottom, chamfer = section((py - y0) / max(y1 - y0, 1e-9))
            across = abs(px - middle)
            if across > half:
                return False
            cut = max(0.0, chamfer - (half - across))
            return bottom + cut <= pz <= top - cut

        reach = max(section(t / 20)[0] for t in range(21))
        tops = [section(t / 20)[1] for t in range(21)]
        bottoms = [section(t / 20)[2] for t in range(21)]
        self.fill(inside, (middle - reach, middle + reach, y0, y1, min(bottoms), max(tops)), material, mirror)

    def nacelle(
        self, x: float, y: tuple[float, float], z: float, radius: float, material: str, mirror: bool = True
    ) -> None:
        """A pod along y, octagonal, around x and height z (units)."""

        def inside(px: float, py: float, pz: float) -> bool:
            dx, dz = abs(px - x), abs(pz - z)
            return y[0] <= py <= y[1] and max(dx, dz) <= radius and dx + dz <= radius * 1.42

        self.fill(inside, (x - radius, x + radius, y[0], y[1], z - radius, z + radius), material, mirror)

    def plate(
        self,
        outline: list[tuple[float, float]],
        z: tuple[float, float] | Callable[[float, float], tuple[float, float]],
        material: str,
        mirror: bool = True,
    ) -> None:
        """A flat shape (a wing): inside the polygon `outline` ((x, y) corners, units), from z[0] to z[1]; `z` can
        also depend on the place, (x, y) -> (bottom, top), for wings that rise or taper.
        """
        xs, ys = [p[0] for p in outline], [p[1] for p in outline]
        if isinstance(z, tuple):
            fixed = z

            def heights(_x: float, _y: float) -> tuple[float, float]:
                return fixed

        else:
            heights = z

        def inside(px: float, py: float, pz: float) -> bool:
            if not _inside(px, py, outline):
                return False
            bottom, top = heights(px, py)
            return bottom - 0.5 <= pz <= top + 0.5

        samples = [heights(x, y) for x in xs for y in ys]
        low = min(bottom for bottom, _ in samples) - 1
        high = max(top for _, top in samples) + 1
        self.fill(inside, (min(xs), max(xs), min(ys), max(ys), low, high), material, mirror)

    def fin(
        self, x: float, outline: list[tuple[float, float]], material: str, thickness: float = 0.5, mirror: bool = True
    ) -> None:
        """An upright plate at x: `outline` is its side view ((y, z) corners, units)."""
        ys, zs = [p[0] for p in outline], [p[1] for p in outline]

        def inside(px: float, py: float, pz: float) -> bool:
            return abs(px - x) <= thickness / 2 and _inside(py, pz, outline)

        self.fill(inside, (x - thickness, x + thickness, min(ys), max(ys), min(zs), max(zs)), material, mirror)

    def paint(self, where: Inside, material: str, mirror: bool = True) -> None:
        """Recolor the cubes (not empty space) whose middle is where `where(x, y, z)` holds (units)."""
        s = self.scale
        for i, j, k in list(self.cells):
            if where((i + 0.5) / s, (j + 0.5) / s, k / s + 1e-6) or (
                mirror and where((self.width * s - i - 0.5) / s, (j + 0.5) / s, k / s + 1e-6)
            ):
                self.cells[i, j, k] = material

    def carve(self, where: Inside) -> None:
        s = self.scale
        for i, j, k in list(self.cells):
            if where((i + 0.5) / s, (j + 0.5) / s, k / s + 1e-6):
                del self.cells[i, j, k]

    # -- details

    def tops(self) -> dict[tuple[int, int], int]:
        """The highest cube of each column."""
        result: dict[tuple[int, int], int] = {}
        for i, j, k in self.cells:
            if k > result.get((i, j), -(10**6)):
                result[i, j] = k
        return result

    def finish(self, seams: Iterable[float] = (), keep: frozenset[str] = frozenset()) -> None:
        """Panel seams across the hull at rows `seams` (units: the top cube of each plated column there is recessed a
        cube, darker), lighter top edges where the hull drops away, darker undersides. Materials in `keep` (glass,
        lights, paint...) are left alone.
        """
        s = self.scale
        tops = self.tops()
        for row in seams:
            j = math.floor(row * s)
            for (i, jj), top in list(tops.items()):
                if jj == j and top > 0 and self.cells.get((i, j, top)) in PLATING:
                    del self.cells[i, j, top]
                    self.cells.setdefault((i, j, top - 1), "seam")
                    self.cells[i, j, top - 1] = "seam"
        tops = self.tops()
        for (i, j), top in tops.items():
            if self.cells.get((i, j, top)) != "hull":
                continue
            around = [tops.get((i + di, j + dj), -(10**6)) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if min(around) <= top - max(2, s):  # an edge with a drop next to it
                self.cells[i, j, top] = "hull_light"
        for cell, material in list(self.cells.items()):
            if material in keep or material not in PLATING:
                continue
            if cell[2] < 0 and (cell[0], cell[1], cell[2] - 1) not in self.cells:
                self.cells[cell] = "hull_dark"

    # -- writing out

    def drawing(self, engines: list[dict] | None = None) -> dict:
        """The game's 3D drawing: layers from the top (nearest the camera) down, the middle one on z = 0. Engines
        are given in units and written in the drawing's cubes.
        """
        s = self.scale
        used = sorted(set(self.cells.values()))
        letters = string.ascii_letters
        char = {material: letters[index] for index, material in enumerate(used)}
        extent = max((abs(k) for _, _, k in self.cells), default=0)
        layers = [
            [
                "".join(char[self.cells[i, j, k]] if (i, j, k) in self.cells else "." for i in range(self.width * s))
                for j in range(self.height * s)
            ]
            for k in range(extent, -extent - 1, -1)
        ]
        palette = {char[m]: {"color": [round(c, 3) for c in self.materials[m]]} for m in used}
        result: dict = {"layers": layers, "palette": palette}
        if s != 1:
            result["scale"] = s
        if engines:
            result["engines"] = [_scaled_engine(engine, s) for engine in engines]
        return result

    def save(self, path: Path, engines: list[dict] | None = None) -> None:
        path.write_text(_dump(self.drawing(engines)) + "\n")


def _scaled_engine(engine: dict, scale: int) -> dict:
    """An engine in units -> in the drawing's cubes (a cube's middle: unit column 5 is cubes 10 and 11 at scale 2,
    so its middle is 10.5).
    """
    result = dict(engine)
    for key in ("x", "y"):
        result[key] = round((engine[key] + 0.5) * scale - 0.5, 3)
    for key in ("width", "length"):
        result[key] = round(engine[key] * scale, 3)
    if "z" in engine:
        result["z"] = round(engine["z"] * scale, 3)
    return result


def _inside(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    inside = False
    for (x1, y1), (x2, y2) in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _dump(drawing: dict) -> str:
    """JSON with each row of a layer on its own line (readable as pictures)."""
    head = {key: value for key, value in drawing.items() if key not in ("layers", "palette", "engines")}
    lines = ["{"]
    lines += [f'  "{key}": {json.dumps(value)},' for key, value in head.items()]
    lines.append('  "layers": [')
    for index, layer in enumerate(drawing["layers"]):
        rows = ",\n".join(f'      "{row}"' for row in layer)
        lines.append("    [\n" + rows + "\n    ]" + ("," if index < len(drawing["layers"]) - 1 else ""))
    lines.append("  ],")
    palette = ",\n".join(f'    "{key}": {json.dumps(value)}' for key, value in drawing["palette"].items())
    lines.append('  "palette": {\n' + palette + "\n  }" + ("," if "engines" in drawing else ""))
    if "engines" in drawing:
        engines = ",\n".join(f"    {json.dumps(engine)}" for engine in drawing["engines"])
        lines.append('  "engines": [\n' + engines + "\n  ]")
    lines.append("}")
    return "\n".join(lines)
