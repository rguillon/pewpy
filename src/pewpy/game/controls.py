"""What the player does with the controls, each frame."""

from dataclasses import dataclass


@dataclass
class Controls:
    """What the player asks for this frame: where to move (-1 to 1 on each axis), whether to fire."""

    move_x: float = 0.0
    move_y: float = 0.0
    fire: bool = False
