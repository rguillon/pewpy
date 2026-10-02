"""Writing the game's YAML files, readable by people: short lists and mappings of plain values on one line."""

from pathlib import Path
from typing import Any

import yaml

FLOW_WIDTH = 80  # a list or mapping of plain values this short (written on one line) stays on one line
NO_WRAP = 1_000_000  # long lines are not cut


class _Dumper(yaml.SafeDumper):
    """Block style, except for the short lists and mappings of plain values (a point, an engine, a color)."""

    def represent_sequence(self, tag: str, sequence: Any, flow_style: bool | None = None) -> yaml.SequenceNode:  # noqa: ANN401, ARG002
        return super().represent_sequence(tag, sequence, flow_style=_flow(sequence))

    def represent_mapping(self, tag: str, mapping: Any, flow_style: bool | None = None) -> yaml.MappingNode:  # noqa: ANN401, ARG002
        return super().represent_mapping(tag, mapping, flow_style=_flow(mapping))

    def ignore_aliases(self, data: Any) -> bool:  # noqa: ANN401, ARG002
        return True  # no anchors (&id001): every value written out where it is


def _flow(data: list | dict) -> bool:
    values = data.values() if isinstance(data, dict) else data
    if not data or any(isinstance(value, (list, dict)) for value in values):
        return not data  # empty: [] or {}
    return len(yaml.safe_dump(data, default_flow_style=True, width=NO_WRAP)) <= FLOW_WIDTH


def dump_yaml(data: Any) -> str:  # noqa: ANN401
    """Return the YAML text of `data`, keys in their order."""
    return yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=NO_WRAP)


def write_yaml(path: Path, data: Any) -> None:  # noqa: ANN401
    """Write `data` to the YAML file `path`."""
    path.write_text(dump_yaml(data))
