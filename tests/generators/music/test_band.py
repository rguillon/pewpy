from pewpy.audio.midi import DRUMS
from pewpy.audio.synth import instrument
from pewpy.audio.synth.instruments import BASS as BASS_SOUND
from pewpy.audio.synth.instruments import BRASS as BRASS_SOUND
from pewpy.audio.synth.instruments import LEAD as LEAD_SOUND
from pewpy.audio.synth.instruments import PAD as PAD_SOUND
from pewpy.audio.synth.instruments import PLUCK
from pewpy.generators.music.band import ARP, BASS, BRASS, LEAD, PAD, PROGRAMS, TOMS, VOLUMES


def test_every_instrument_has_its_own_channel_and_sounds_as_its_name_says() -> None:
    channels = (BASS, PAD, ARP, LEAD, BRASS)
    assert len(set(channels)) == len(channels)
    assert DRUMS not in channels
    sounds = {BASS: BASS_SOUND, PAD: PAD_SOUND, ARP: PLUCK, LEAD: LEAD_SOUND, BRASS: BRASS_SOUND}
    assert all(instrument(PROGRAMS[channel]) is sound for channel, sound in sounds.items())


def test_every_channel_has_a_volume_and_the_toms_go_down() -> None:
    assert set(VOLUMES) == {BASS, PAD, ARP, LEAD, BRASS, DRUMS}
    assert all(0 < volume <= 127 for volume in VOLUMES.values())
    assert list(TOMS) == sorted(TOMS, reverse=True)
