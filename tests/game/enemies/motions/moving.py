"""A plain enemy to move, and moving it with a motion frame by frame."""

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.enemies.spec import EnemySpec
from pewpy.game.entities import Entity

DT = 1 / 60
TARGET = Entity(x=0.3, y=-0.75)
SCROLL = 0.2


def enemy(**fields: object) -> Enemy:
    """Make a small enemy with these fields."""
    made = Enemy.from_spec(EnemySpec(kind="test", width=0.1, height=0.1))
    for name, value in fields.items():
        setattr(made, name, value)
    return made


def move(moving: Enemy, motion: Motion, seconds: float = DT, target: Entity = TARGET) -> None:
    """Run the motion and move, for `seconds`."""
    for _ in range(max(1, round(seconds / DT))):
        moving.age += DT
        motion.apply(moving, DT, target, SCROLL)
        moving.move(DT)
