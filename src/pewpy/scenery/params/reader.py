"""Building the parameters from the YAML data.

Merging a level's values over its preset's, checking and converting them to the dataclasses.
"""

import types
from dataclasses import fields, is_dataclass
from typing import Any, Union, get_args, get_origin, get_type_hints

from pewpy.scenery.params.types import SceneryError

# What depends on which generator or painter an object names: when `over` names another one, these are replaced by
# `over`'s (the new one's numbers and colors), not merged with the old one's.
DEPENDS_ON = {"landscape": ("shape",), "style": ("colors",), "kind": ("layout", "knobs", "colors")}


def merge(base: Any, over: Any) -> Any:  # noqa: ANN401 - decoded YAML
    """`over` on top of `base`: objects merged key by key, anything else replaced."""
    if isinstance(base, dict) and isinstance(over, dict):
        merged = dict(base)
        for key, value in over.items():
            merged[key] = merge(base[key], value) if key in base else value
        for name, dependents in DEPENDS_ON.items():
            if name in base and name in over and base[name] != over[name]:
                for key in dependents:
                    if key in base:
                        merged[key] = over.get(key, {})
        return merged
    return over


def _number(value: object, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SceneryError(where, f"expected a number, not {value!r}")
    return float(value)


def _convert(kind: Any, value: Any, where: str) -> Any:  # noqa: ANN401, C901, PLR0911, PLR0912 - one case per type
    """`value` (decoded YAML) as `kind`, a type of the dataclasses above."""
    origin, args = get_origin(kind), get_args(kind)
    if origin in (Union, types.UnionType):  # X | None
        if value is None:
            return None
        return _convert(next(arg for arg in args if arg is not type(None)), value, where)
    if value is None:
        raise SceneryError(where, "missing (null)")
    if is_dataclass(kind) and isinstance(kind, type):
        return build(kind, value, where)
    if kind is float:
        return _number(value, where)
    if kind is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SceneryError(where, f"expected a whole number, not {value!r}")
        return value
    if kind is str:
        if not isinstance(value, str):
            raise SceneryError(where, f"expected a name, not {value!r}")
        return value
    if origin is tuple:
        if not isinstance(value, list):
            raise SceneryError(where, f"expected a list, not {value!r}")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_convert(args[0], item, f"{where}[{i}]") for i, item in enumerate(value))
        if len(value) != len(args):
            raise SceneryError(where, f"expected {len(args)} values, not {len(value)}")
        return tuple(_convert(arg, item, f"{where}[{i}]") for i, (arg, item) in enumerate(zip(args, value)))  # noqa: B905
    if origin is dict:
        if not isinstance(value, dict):
            raise SceneryError(where, f"expected an object, not {value!r}")
        return {key: _convert(args[1], item, f"{where}.{key}") for key, item in value.items()}
    if kind is Any:
        return value
    raise SceneryError(where, f"can't read a {kind}")


def build(cls: Any, data: Any, where: str = "", given: dict[str, Any] | None = None) -> Any:  # noqa: ANN401
    """Build a dataclass from decoded YAML: every field there, nothing else (but the fields `given`)."""
    if not isinstance(data, dict):
        raise SceneryError(where, f"expected an object, not {data!r}")
    given = given or {}
    hints = get_type_hints(cls)
    names = {field.name for field in fields(cls)} - set(given)
    unknown = set(data) - names
    if unknown:
        raise SceneryError(where, f"unknown keys {sorted(unknown)}, expected some of {sorted(names)}")
    missing = names - set(data)
    if missing:
        raise SceneryError(where, f"missing {sorted(missing)}")
    values = {name: _convert(hints[name], data[name], f"{where}.{name}" if where else name) for name in names}
    return cls(**values, **given)
