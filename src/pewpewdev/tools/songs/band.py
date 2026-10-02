"""The band: a channel and a General MIDI program per instrument, their volumes, the drums' notes."""

from pewpy.audio.midi import DRUMS

BASS, PAD, ARP, LEAD, BRASS = 0, 1, 2, 3, 4  # channels
PROGRAMS = {BASS: 38, PAD: 89, ARP: 80, LEAD: 81, BRASS: 61}  # synth bass 1, warm pad, square, saw lead, brass
VOLUMES = {BASS: 100, PAD: 90, ARP: 80, LEAD: 105, BRASS: 95, DRUMS: 110}
KICK, SNARE, CLAP, CLOSED_HAT, OPEN_HAT, CRASH = 36, 38, 39, 42, 46, 49
TOMS = (50, 48, 47, 45, 43, 41)  # high to low
