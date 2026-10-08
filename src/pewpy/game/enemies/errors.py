"""Mistakes in the enemies' descriptions (see spec.py)."""


class EnemySpecError(Exception):
    """An enemy's description is wrong."""

    def __init__(self, source: str, message: str) -> None:
        """Say which description (`source`) is wrong, and how (`message`)."""
        super().__init__(f"{source}: {message}")


class UnknownNameError(ValueError):
    """A name (of a kind of enemy, a motion, an action...) isn't known."""

    def __init__(self, what: str, name: object) -> None:
        """Say that the unknown `name` was given as a `what` (a kind of enemy, a motion...)."""
        super().__init__(f"unknown {what} {name!r}")


class UnknownConditionError(UnknownNameError):
    """An exit's condition isn't known."""

    def __init__(self, name: str) -> None:
        """Say that no exit condition goes by `name`."""
        super().__init__("exit condition", name)


class FlagError(ValueError):
    """A flag (a condition written `name: true`) was given another value."""

    def __init__(self, name: str) -> None:
        """Say that the flag `name` can only be set to true."""
        super().__init__(f"{name} can only be true")
