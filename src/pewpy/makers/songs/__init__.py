"""The game's synthwave songs, composed as MIDI (the Dev menu's music browser makes them).

Every song is the same recipe, in a minor key: a chord progression, a bar per chord (two when slow); sections in
turn (an intro, a verse with the drums, bass and arpeggio, a chorus with the lead tune, a breakdown, the chorus
again), a tom fill closing each, a crash opening the next. The tune is a two-bar motif, repeated and varied, chord
notes on the beats and scale steps between. Songs loop (a "loop" marker where they end); the two jingles don't.

The plans are in plans.py, the harmony in harmony.py, the band (channels, programs, drums) in band.py, each part
(pad, bass, arpeggio, drums, brass, tune) in its own module in tracks/; compose.py puts a song together.
"""
