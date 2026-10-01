"""Evolution strategies (OpenAI's ES): improving a brain's weights from how a crowd of noisy copies of it fare.

Each generation tries the weights plus and minus POPULATION // 2 random nudges (mirrored, so the luck of a nudge
cancels out), ranks every try by its fitness, and moves the weights towards the nudges that did better, with Adam
steps. Only numbers in here: the game is played elsewhere (learning.py).
"""

from dataclasses import dataclass, field

import numpy as np

POPULATION = 64  # tries per generation (even)
NOISE = 0.05  # how big the nudges are
LEARNING_RATE = 0.06
WEIGHT_DECAY = 0.005  # keeps the weights small
BETAS = (0.9, 0.999)  # Adam's


def ranks(fitness: np.ndarray) -> np.ndarray:
    """Fitness as centered ranks, from -0.5 (the worst) to 0.5 (the best): only the order counts, not how much."""
    order = np.empty(len(fitness))
    order[np.argsort(fitness, kind="stable")] = np.arange(len(fitness))
    return order / max(len(fitness) - 1, 1) - 0.5


@dataclass
class Evolution:
    weights: np.ndarray
    rng: np.random.Generator
    population: int = POPULATION
    noise: float = NOISE
    learning_rate: float = LEARNING_RATE
    generation: int = 0
    moment: np.ndarray = field(init=False)
    velocity: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        if self.population < 2 or self.population % 2:
            msg = "the population must be even"
            raise ValueError(msg)
        self.moment = np.zeros_like(self.weights)
        self.velocity = np.zeros_like(self.weights)

    def ask(self) -> tuple[np.ndarray, list[np.ndarray]]:
        """This generation's nudges (half of them, the other half are their opposites) and the weights to try."""
        nudges = self.rng.standard_normal((self.population // 2, len(self.weights)))
        tries = [self.weights + sign * self.noise * nudge for nudge in nudges for sign in (1.0, -1.0)]
        return nudges, tries

    def tell(self, nudges: np.ndarray, fitness: np.ndarray) -> None:
        """Move the weights from the tries' fitness (in the order `ask` gave them)."""
        shaped = ranks(np.asarray(fitness, dtype=float)).reshape(-1, 2)
        gradient = (shaped[:, 0] - shaped[:, 1]) @ nudges / (self.population * self.noise)
        gradient -= WEIGHT_DECAY * self.weights
        self.generation += 1
        beta1, beta2 = BETAS
        self.moment = beta1 * self.moment + (1 - beta1) * gradient
        self.velocity = beta2 * self.velocity + (1 - beta2) * gradient**2
        corrected = self.learning_rate * np.sqrt(1 - beta2**self.generation) / (1 - beta1**self.generation)
        self.weights = self.weights + corrected * self.moment / (np.sqrt(self.velocity) + 1e-8)
