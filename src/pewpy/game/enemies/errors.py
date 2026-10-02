"""Mistakes in the enemies' descriptions (see spec.py)."""


class EnemySpecError(Exception):
    def __init__(self, source: str, message: str) -> None:
        super().__init__(f"{source}: {message}")


class UnknownNameError(ValueError):
    def __init__(self, what: str, name: object) -> None:
        super().__init__(f"unknown {what} {name!r}")


class UnknownConditionError(UnknownNameError):
    def __init__(self, name: str) -> None:
        super().__init__("exit condition", name)


class FlagError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"{name} can only be true")
