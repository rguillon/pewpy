from panda3d.core import NodePath

from pewpy.ui.music_browser_view import KEYS, MusicBrowserView


def test_the_music_browser_says_which_song_and_whats_going_on() -> None:
    view = MusicBrowserView(NodePath("aspect2d"))
    assert view.keys.getText() == KEYS
    view.describe("LEVEL 1-1", "fast and bright", "rendering")
    assert (view.title.getText(), view.details.getText(), view.status.getText()) == (
        "LEVEL 1-1",
        "fast and bright",
        "rendering",
    )


def test_the_music_browser_says_whether_the_song_plays() -> None:
    view = MusicBrowserView(NodePath("aspect2d"))
    view.show_playing("PLAYING")
    view.show_playing("PLAYING")
    assert view.playing.getText() == "PLAYING"
    view.show_playing("")
    assert view.playing.getText() == ""
