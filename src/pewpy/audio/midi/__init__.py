"""Standard MIDI files: songs as notes, read and written. No Panda3D.

Only what songs need: notes, the instrument of each channel (program change), the channel volume (controller 7)
and the tempo (with changes). Channel 9 (the tenth) holds the drums, as in General MIDI.
song.py has the song, writer.py and reader.py the file format.
"""

from pewpy.audio.midi.reader import read
from pewpy.audio.midi.song import DRUMS, TICKS_PER_BEAT, MidiError, Note, Song
from pewpy.audio.midi.writer import write

__all__ = [
    "DRUMS",
    "TICKS_PER_BEAT",
    "MidiError",
    "Note",
    "Song",
    "read",
    "write",
]
