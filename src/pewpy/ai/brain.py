"""The AI's neural network: a small multilayer perceptron in numpy.

All its weights are in one flat vector, with a direct path from its inputs to its outputs besides the hidden layer
(so a simple rule, like following the radar's safest way, is only a few weights away, the hidden layer learning the
rest).

From what the AI sees (sensors.py) to what it does: OUTPUTS numbers, the stick (x, y, from -1 to 1) and the fire
button (fires above 0). The weapon is not its choice: the pilot fires the strongest one (pilot.py).
"""

from dataclasses import dataclass

import numpy as np

from pewpy.ai import sensors

HIDDEN = (24,)  # neurons in each hidden layer
OUTPUTS = 3
FIRE_BIAS = -1.0  # a new brain starts with the fire button released...
FIRE_GAIN = 2.0  # ...but held while an enemy can be hurt: firing at nothing only puts the repairs off
RADAR_GAIN = 3.0  # a new brain starts flying the radar's move to aim, the stick this far over (clamped to 1)
OUTPUT_NOISE = 0.03  # how much its hidden layer moves the outputs at first (scaled to its size): little, its hand-made
# start (the radar to the stick, the fire button held) leads


def shapes(inputs: int = sensors.SIZE, hidden: tuple[int, ...] = HIDDEN) -> list[tuple[int, int]]:
    """Each layer's weight matrix shape (its biases are one more row), then the direct path's (no biases)."""
    sizes = [inputs, *hidden, OUTPUTS]
    return [*((sizes[i] + 1, sizes[i + 1]) for i in range(len(sizes) - 1)), (inputs, OUTPUTS)]


def parameter_count(inputs: int = sensors.SIZE, hidden: tuple[int, ...] = HIDDEN) -> int:
    """Count the weights (biases included) of a brain with these inputs and hidden layers."""
    return sum(rows * columns for rows, columns in shapes(inputs, hidden))


@dataclass
class Brain:
    """A brain: its weights, flat, and the shape of its layers."""

    weights: np.ndarray  # flat: every layer's weights and biases one after the other
    hidden: tuple[int, ...] = HIDDEN
    inputs: int = sensors.SIZE

    def __post_init__(self) -> None:
        """Check the weights fit the shape and cut them into the layers' matrices."""
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
        """Make a new brain that dodges and aims before it learns anything.

        Its weights are small and random (scaled for each layer's inputs; the outputs' OUTPUT_NOISE), with no
        biases but FIRE_BIAS, and the direct path closed but from the radar's move to aim to the stick
        (RADAR_GAIN) and from there being something to shoot to the fire button (FIRE_GAIN).
        """
        parts = []
        layers = shapes(sensors.SIZE, hidden)
        for rows, columns in layers[:-1]:
            layer = rng.normal(0.0, 1.0 / np.sqrt(rows - 1), (rows, columns))
            layer[-1] = 0.0
            parts.append(layer.ravel())
        out = parts[-1].reshape(-1, OUTPUTS)
        out[:-1] *= OUTPUT_NOISE
        out[-1, 2] = FIRE_BIAS
        direct = np.zeros((sensors.SIZE, OUTPUTS))
        direct[sensors.AIM, 0] = direct[sensors.AIM + 1, 1] = RADAR_GAIN
        direct[sensors.SHOOTABLE, 2] = FIRE_GAIN
        parts.append(direct.ravel())
        return cls(np.concatenate(parts), hidden)

    def think(self, view: np.ndarray) -> np.ndarray:
        """Return the OUTPUTS numbers for what the AI sees."""
        *layers, direct = self.layers
        signal = view
        for index, layer in enumerate(layers):
            signal = signal @ layer[:-1] + layer[-1]
            if index < len(layers) - 1:
                signal = np.tanh(signal)
        return signal + view @ direct
