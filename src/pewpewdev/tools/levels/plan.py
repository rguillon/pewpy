"""What a world's plan is: its ground and its levels, each with its bosses and its looks."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LevelPlan:
    name: str
    mini_boss: str  # halfway
    final_boss: str  # at the end
    time_of_day: str = "day"
    clouds: float = 0.0
    seed: int = 0  # the background's layout (0: one of its own)
    scenery: dict[str, Any] = field(default_factory=dict)  # changes to the world's preset


@dataclass(frozen=True)
class WorldPlan:
    name: str
    background: str  # its ground: a preset of levels/sceneries.json
    levels: tuple[LevelPlan, ...]
    ground_units: bool = True  # False over water: no tanks or turrets
