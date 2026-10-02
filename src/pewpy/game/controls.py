"""What the player does with the controls, each frame."""

from dataclasses import dataclass


@dataclass
class Controls:
    move_x: float = 0.0
    move_y: float = 0.0
    fire: bool = False
