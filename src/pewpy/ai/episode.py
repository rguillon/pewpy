"""Playing a level with a pilot, headless, as fast as the computer goes.

Training plays with one life (an episode ends at the first death) and grades the run (`fitness`); rating plays by
the game's rules (its lives, restarting the level after each death) and only asks whether the level was cleared.
"""

from dataclasses import dataclass

from pewpy.ai.brain import Brain
from pewpy.ai.pilot import Pilot
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.level import Level
from pewpy.game.player import SHIPS
from pewpy.game.world import World

DT = 1 / 60
OVERTIME = 60.0  # seconds per boss before giving up (an AI that only dodges a boss forever)

# Grading a training run, as a weighted sum: how far into the level it got (in seconds on the waves' clock, which
# waits while a boss is fought: dodging a boss forever earns nothing), its score, how much of each boss it destroyed
# (the mini boss as the final one), and clearing the level (more with health left).
PER_SECOND = 1.0
PER_POINT = 1 / 250
BOSS_DAMAGE = 60.0  # per boss
CLEARED = 150.0
HEALTH_LEFT = 30.0


@dataclass(frozen=True)
class Outcome:
    cleared: bool
    time: float  # seconds played, every life included
    progress: float  # how far into the level (its last life), from 0 to 1 (the final boss's arrival), then to 2 (the
    # final boss destroyed)
    score: int
    lives_lost: int
    health_left: float  # share of the last life's health
    advanced: float = 0.0  # seconds on the waves' clock (its last life)
    bosses: float = 0.0  # the bosses destroyed (its last life), a damaged one counting for the share destroyed

    @property
    def fitness(self) -> float:
        bonus = CLEARED + HEALTH_LEFT * self.health_left if self.cleared else 0.0
        return PER_SECOND * self.advanced + PER_POINT * self.score + BOSS_DAMAGE * self.bosses + bonus


def boss_time(level: Level) -> float:
    """When the final boss comes, on the waves' clock (see World.wave_time)."""
    return max((wave.time for wave in level.waves), default=0.0)


def play(level: Level, brain: Brain, ship: str, seed: int, lives: int = 1) -> Outcome:
    """Play `level` with `brain` flying `ship` until it is cleared, the lives are gone or time is up."""
    world = World(level, seed=seed, lives=lives, ship=SHIPS[ship])
    pilot = Pilot(brain)
    arrival = boss_time(level)
    limit = arrival + OVERTIME * max(sum(wave.enemy in BOSSES for wave in level.waves), 1)
    boss_seen = 0.0
    damage: dict[int, float] = {}  # this life's bosses: the share of each destroyed
    life = world.player
    played = 0.0
    while not world.completed and not world.game_over and world.time < limit:
        world.update(DT, pilot.fly(world))
        played += DT
        if world.player is not life:  # a life lost: the level starts again
            life, damage, boss_seen = world.player, {}, 0.0
        boss = world.boss
        if boss is not None:
            damage[id(boss)] = max(damage.get(id(boss), 0.0), 1.0 - boss.health_fraction)
            if not any(spawn.enemy in BOSSES for spawn in world.pending_spawns):  # the final boss
                boss_seen = max(boss_seen, 1.0 - boss.health_fraction)
    if world.completed:
        progress = 2.0
        damage = dict.fromkeys(damage, 1.0)  # the last blow may not show: the boss is gone in that update
    else:
        reached = min(world.wave_time / arrival, 1.0) if arrival else 1.0
        progress = reached + boss_seen if reached >= 1.0 or boss_seen else reached
    return Outcome(
        cleared=world.completed,
        time=played,
        progress=progress,
        score=world.score,
        lives_lost=lives - max(world.lives, 0),
        health_left=max(world.player.health, 0.0) / world.ship.health if world.completed else 0.0,
        advanced=world.wave_time,
        bosses=sum(damage.values()),
    )
