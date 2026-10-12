from panda3d.core import NodePath

from pewpy.ui.ai_panel import AIPanel, playing_text


def test_the_text_tells_how_the_games_went() -> None:
    assert "Games" not in playing_text(None, "here", "1-1", games=1, cleared=0, best=0)
    text = playing_text(3, "here", "2-1", games=5, cleared=1, best=2)
    assert "Games from 2-1: 4, 2-1 cleared in 1 (25%)" in text
    assert "Best game: 2 levels cleared" in text


def test_the_text_says_which_brain_plays_and_what_is_on_screen() -> None:
    assert "no brain yet" in playing_text(None, "1-1", "1-1", games=1, cleared=0, best=0)
    text = playing_text(7, "1-2", "1-1", games=2, cleared=1, best=1)
    assert "generation 7" in text
    assert "On screen: 1-2" in text
    assert "Best game: 1 level cleared" in text


def test_the_panel_shows_its_text_until_hidden() -> None:
    panel = AIPanel(NodePath("aspect2d"))
    assert panel.text.isHidden()
    panel.show("playing")
    assert panel.text.getText() == "playing"
    assert not panel.text.isHidden()
    panel.show("playing")
    panel.hide()
    assert panel.text.isHidden()
