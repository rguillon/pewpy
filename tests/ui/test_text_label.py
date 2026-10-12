import pytest
from panda3d.core import NodePath

from pewpy.ui.menu_view import TEXT_SHADOW
from pewpy.ui.text_label import TextsView, centered

WHITE = (1.0, 1.0, 1.0, 1.0)


def test_a_centered_text_is_empty_until_told_and_has_a_shadow() -> None:
    text = centered(NodePath("aspect2d"), 0.3, 0.05, WHITE)
    assert text.getText() == ""
    assert text.getTextPos() == (0, 0.3)
    assert tuple(text.textNode.getShadowColor()) == pytest.approx(TEXT_SHADOW)


def test_a_view_keeps_its_texts_and_takes_them_away() -> None:
    parent = NodePath("aspect2d")
    view = TextsView(parent, "texts")
    view.centered_text(0.1, 0.05, WHITE)
    view.centered_text(-0.1, 0.05, WHITE, wordwrap=20)
    assert len(view.texts) == 2
    assert view.texts[1].textNode.getWordwrap() == 20
    view.destroy()
    assert parent.find("texts").isEmpty()
