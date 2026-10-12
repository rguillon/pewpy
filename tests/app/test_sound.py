from pewpy.app import PewPewApp, keys
from tests.app.driving import press


def test_the_music_key_turns_the_music_off_and_on(app: PewPewApp) -> None:
    on = app.audio.music_on
    press(app, keys.MUSIC_KEY)
    assert app.audio.music_on is not on
    press(app, keys.MUSIC_KEY)
    assert app.audio.music_on is on
