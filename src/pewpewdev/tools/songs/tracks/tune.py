"""The lead's tune: a motif, repeated and varied."""

from pewpewdev.tools.songs.band import LEAD
from pewpewdev.tools.songs.harmony import RHYTHMS
from pewpewdev.tools.songs.writer import Writer, near


def tune_pitch(writer: Writer, chord_tones: set[int], on_beat: bool) -> int:
    """Pick the next note of the tune: a chord note near the last one on the beat, else a step along the scale."""
    previous = writer.last_tune
    scale = writer.scale()
    candidates = [pitch for pitch in scale if 67 <= pitch <= 86]
    if on_beat:
        choices = [pitch for pitch in candidates if pitch % 12 in chord_tones and abs(pitch - previous) <= 7]
        choices = choices or [pitch for pitch in candidates if pitch % 12 in chord_tones]
        weights = [1.0 / (1 + abs(pitch - previous)) ** 0.7 for pitch in choices]
        return writer.rng.choices(choices, weights)[0]
    index = min(range(len(candidates)), key=lambda i: abs(candidates[i] - previous))
    step = writer.rng.choice((-2, -1, -1, 1, 1, 2))
    return candidates[max(0, min(len(candidates) - 1, index + step))]


def make_motif(writer: Writer) -> list[tuple[float, float]]:
    """Two bars of rhythm for the tune, the second ending on a long note."""
    first = writer.rng.choice(RHYTHMS)
    second = writer.rng.choice((((0, 1.5), (1.5, 2.5)), ((0, 0.5), (0.5, 0.5), (1, 3)), ((0, 1), (1, 3))))
    return [*first, *((4 + at, length) for at, length in second)]


def tune(writer: Writer, start: float, chords: list[tuple[int, tuple[int, ...]]], bars_per_chord: int) -> None:
    """Write the lead's tune over the chorus: a motif four times, the third varied, the last ending on the tonic."""
    motif = make_motif(writer)
    variation = list(writer.rng.choice(RHYTHMS)) + [(4 + at, length) for at, length in motif if at >= 4]
    total_bars = len(chords) * bars_per_chord
    phrases = max(1, total_bars // 2)
    remembered: list[int] = []
    for phrase in range(phrases):
        rhythm = variation if phrase % 4 == 2 else motif
        repeat = phrase % 2 == 1 and remembered and phrase % 4 != 2
        for index, (at, length) in enumerate(rhythm):
            beat = phrase * 8 + at
            root, shape = chords[min(int(beat // (4 * bars_per_chord)), len(chords) - 1)]
            tones = {(root + step) % 12 for step in shape}
            last_note = phrase == phrases - 1 and index == len(rhythm) - 1
            if last_note:
                pitch = near(writer.tonic, writer.last_tune)
            elif repeat and index < len(remembered) - 2:
                pitch = remembered[index]  # the answer starts like the call
                if pitch % 12 not in tones and at % 1 == 0:
                    pitch = tune_pitch(writer, tones, on_beat=True)
            else:
                pitch = tune_pitch(writer, tones, on_beat=at % 1 == 0)
            if phrase % 2 == 0:
                remembered = [*remembered[:index], pitch] if index else [pitch]
            writer.last_tune = pitch
            writer.add(LEAD, start + beat, length * 0.95, pitch, 108 if at % 1 == 0 else 94)
