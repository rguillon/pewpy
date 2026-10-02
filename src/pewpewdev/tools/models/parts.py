"""What the recipes share: engines, running lights, ribbed nacelles, ramps."""

from pewpewdev.tools.models.registry import MODELS
from pewpewdev.tools.models.sculpt import Model
from pewpy.data import read_yaml


def engines_of(name: str, z: float | None = None) -> list[dict]:
    """Return the model's engines as in its file now (their flames stay where they were), maybe raised to `z`."""
    data = read_yaml(MODELS / f"{name}.yaml")
    engines = [dict(engine) for engine in data.get("engines", [])]
    if z is not None:
        for engine in engines:
            engine["z"] = z
    return engines


def ramp(t: float, start: float, end: float, until: float = 1.0) -> float:
    """From `start` at t = 0 to `end` at t = `until`, then `end`."""
    return start + (end - start) * min(t / until, 1.0) if until > 0 else end


KEEP = frozenset({"glass", "glint", "paint", "light", "vent", "metal"})


def engine(x: float, y: float, width: float, length: float, towards: str, z: float = 0.0) -> dict:
    """Describe an engine as the drawing files write it."""
    return {"x": x, "y": y, "width": width, "length": length, "towards": towards, "z": z}


def lights(m: Model, x: float, y: tuple[float, float], z: float = 0.0) -> None:
    """Add running lights: small orange marks at x (and its mirror)."""
    m.fill(
        lambda px, py, pz: abs(px - x) < 0.3 and y[0] <= py < y[1] and z <= pz < z + 0.5,
        (x - 1, x + 1, *y, z - 1, z + 1),
        "light",
    )


def ribbed(m: Model, x: float, y: tuple[float, float], z: float, radius: float, step: float = 1.5) -> None:
    """Add a nacelle in hull grey, with dark ribs every `step`."""
    m.nacelle(x, y, z, radius, "hull")
    row = y[0] + step
    while row < y[1] - 0.5:
        m.nacelle(x, (row, row + 0.5), z, radius + 0.15, "frame")
        row += step
