"""Generate the game's synthwave songs as MIDI files (data/music/).

    make songs                               # every song, each from its own seed: the same songs every time
    make songs ARGS="--seed 1234"            # new songs: the same plans (keys, tempos, chords), new tunes
    make songs ARGS="--only boss world_2"    # just these
    make songs ARGS="--wav"                  # also build/music/<name>.wav, as the game plays it, to listen to

(or `uv run python -m pewpewdev.tools.songs ...`). The .mid files open in any MIDI player or music program (General
MIDI: synth bass, warm pad, square arpeggio, saw lead, brass, drums on channel 10); the game plays them with its own
synthesizer (pewpy.audio.synth). A song's own .mid can replace a generated one: the game reads any MIDI file.

Every song is the same recipe, in a minor key: a chord progression, a bar per chord (two when slow); sections in
turn (an intro, a verse with the drums, bass and arpeggio, a chorus with the lead tune, a breakdown, the chorus
again), a tom fill closing each, a crash opening the next. The tune is a two-bar motif, repeated and varied, chord
notes on the beats and scale steps between. Songs loop (a "loop" marker where they end); the two jingles don't.

The plans are in plans.py, the harmony in harmony.py, the band (channels, programs, drums) in band.py, each part
(pad, bass, arpeggio, drums, brass, tune) in its own module in tracks/; compose.py puts a song together.
"""
