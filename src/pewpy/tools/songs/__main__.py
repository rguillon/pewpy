"""Writing the songs (see the package)."""

import argparse
from pathlib import Path

from pewpy.audio import midi, synth
from pewpy.tools import songs
from pewpy.tools.paths import BUILD, DATA
from pewpy.tools.songs.compose import compose
from pewpy.tools.songs.plans import PLANS, Plan

OUT = DATA / "music"
PREVIEWS = BUILD / "music"


def write(plan: Plan, out: Path, seed: int | None = None, wav: Path | None = None) -> Path:
    """Compose a song and write it as MIDI (and as WAV in `wav`, if given); return the MIDI file."""
    song = compose(plan, seed)
    path = out / f"{plan.name}.mid"
    path.write_bytes(midi.write(song, plan.title))
    if wav is not None:
        wav.mkdir(parents=True, exist_ok=True)
        samples = synth.render(midi.read(path.read_bytes()), loop=not plan.jingle)
        (wav / f"{plan.name}.wav").write_bytes(synth.wav_bytes(samples))
    return path


def main() -> None:
    """Compose the songs the command line asks for and write them."""
    parser = argparse.ArgumentParser(description=songs.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, help="new tunes from this seed (default: each song's own)")
    parser.add_argument("--only", nargs="+", choices=[plan.name for plan in PLANS], help="just these songs")
    parser.add_argument("--out", type=Path, default=OUT, help="where (default: the game's music)")
    parser.add_argument("--wav", action="store_true", help=f"also render them to {PREVIEWS}")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for plan in PLANS:
        if args.only and plan.name not in args.only:
            continue
        path = write(plan, args.out, args.seed, PREVIEWS if args.wav else None)
        song = midi.read(path.read_bytes())
        print(f"{plan.name}: {plan.title!r}, {plan.key} minor, {plan.tempo:g} bpm, {song.duration:.0f} s -> {path}")


if __name__ == "__main__":
    main()
