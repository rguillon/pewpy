"""Menus picked with the arrow keys: Up/Down move the highlight, Enter chooses, Escape goes back."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItem:
    label: str
    action: Callable[[], object]


class Menu:
    def __init__(
        self,
        title: str,
        items: list[MenuItem],
        back: Callable[[], object] | None = None,
        selected: int = 0,
    ) -> None:
        """`back` runs on Escape (nothing happens without it). `selected` is the item highlighted at first."""
        if not items:
            raise ValueError("a menu needs at least one item")  # noqa: TRY003
        self.title = title
        self.items = items
        self.back = back
        self.selected = selected % len(items)

    def move(self, step: int) -> None:
        """Move the highlight down (step > 0) or up (step < 0), wrapping around at the ends."""
        self.selected = (self.selected + step) % len(self.items)

    def choose(self) -> None:
        self.items[self.selected].action()

    def go_back(self) -> None:
        if self.back is not None:
            self.back()
