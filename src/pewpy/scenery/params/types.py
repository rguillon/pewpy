"""The types the parameters are made of, and what goes wrong reading them."""

from typing import Any

Color3 = tuple[float, float, float]
Knobs = dict[str, Any]  # a generator's own numbers (and lists), by name


class SceneryError(ValueError):
    """A scenery's parameters are wrong, at `where`."""

    def __init__(self, where: str, problem: str) -> None:
        """Say what's wrong (`problem`) at `where` in the parameters (or nowhere, if `where` is empty)."""
        super().__init__(f"{where}: {problem}" if where else problem)
