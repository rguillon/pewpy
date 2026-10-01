"""The AI's neural network: a small multilayer perceptron in numpy, all its weights in one flat vector, with a
direct path from its inputs to its outputs besides the hidden layer (so a simple rule, like following the radar's
safest way, is only a few weights away, the hidden layer learning the rest).

From what the AI sees (sensors.py) to what it does: OUTPUTS numbers, the stick (x, y, from -1 to 1), the fire button
(fires above 0) and how much it wants each weapon (the highest one is the weapon it picks).
"""

from dataclasses import dataclass

import numpy as np

from pewpy.ai import sensors
from pewpy.game.weapons import WEAPONS

HIDDEN = (24,)  # neurons in each hidden layer
OUTPUTS = 3 + len(WEAPONS)
FIRE_BIAS = 1.0  # a new brain starts with the fire button held: shooting is nearly always right
RADAR_GAIN = 3.0  # a new brain starts flying the radar's safest way, the stick this far over (clamped to 1)


def shapes(inputs: int = sensors.SIZE, hidden: tuple[int, ...] = HIDDEN) -> list[tuple[int, int]]:
    """Each layer's weight matrix shape (its biases are one more row), then the direct path's (no biases)."""
    sizes = [inputs, *hidden, OUTPUTS]
    return [*((sizes[i] + 1, sizes[i + 1]) for i in range(len(sizes) - 1)), (inputs, OUTPUTS)]


def parameter_count(inputs: int = sensors.SIZE, hidden: tuple[int, ...] = HIDDEN) -> int:
    return sum(rows * columns for rows, columns in shapes(inputs, hidden))


@dataclass
class Brain:
    weights: np.ndarray  # flat: every layer's weights and biases one after the other
    hidden: tuple[int, ...] = HIDDEN
    inputs: int = sensors.SIZE

    def __post_init__(self) -> None:
        if self.weights.shape != (parameter_count(self.inputs, self.hidden),):
            msg = f"a brain of this shape has {parameter_count(self.inputs, self.hidden)} weights"
            raise ValueError(msg)
        self.layers = []
        start = 0
        for rows, columns in shapes(self.inputs, self.hidden):
            self.layers.append(self.weights[start : start + rows * columns].reshape(rows, columns))
            start += rows * columns

    @classmethod
    def random(cls, rng: np.random.Generator, hidden: tuple[int, ...] = HIDDEN) -> "Brain":
        """A new brain: small random weights (scaled for each layer's inputs), no biases but FIRE_BIAS, the direct
        path closed but from the radar's safest way to the stick (RADAR_GAIN): it dodges before it learns anything."""
        parts = []
        layers = shapes(sensors.SIZE, hidden)
        for rows, columns in layers[:-1]:
            layer = rng.normal(0.0, 1.0 / np.sqrt(rows - 1), (rows, columns))
            layer[-1] = 0.0
            parts.append(layer.ravel())
        parts[-1].reshape(-1, OUTPUTS)[-1, 2] = FIRE_BIAS
        direct = np.zeros((sensors.SIZE, OUTPUTS))
        direct[sensors.SAFEST, 0] = direct[sensors.SAFEST + 1, 1] = RADAR_GAIN
        parts.append(direct.ravel())
        return cls(np.concatenate(parts), hidden)

    def think(self, view: np.ndarray) -> np.ndarray:
        """The OUTPUTS numbers for what the AI sees."""
        *layers, direct = self.layers
        signal = view
        for index, layer in enumerate(layers):
            signal = signal @ layer[:-1] + layer[-1]
            if index < len(layers) - 1:
                signal = np.tanh(signal)
        return signal + view @ direct
