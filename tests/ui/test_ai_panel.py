from pewpy.ai.learning import Report
from pewpy.ai.rating import Rating
from pewpy.ui.ai_panel import ROWS_PER_COLUMN, learning_text, rating_columns, rating_title


def test_the_learning_text_tells_each_ships_progress():
    text = learning_text(
        "juggernaut",
        {"vanguard": Report("vanguard", 20, 55.0, 30.0, 0.25)},
        {"vanguard": (0.25, 0.6)},
        "On screen: VANGUARD on 1-1 High Peaks",
        None,
    )
    assert "VANGUARD    generation 20  best 55  clears 25% of the levels, gets 60% of the way" in text
    assert "> JUGGERNAUT  waiting for its turn" in text
    assert text.endswith("On screen: VANGUARD on 1-1 High Peaks")
    assert "Stopped: boom" in learning_text("vanguard", {}, {}, "", "boom")


def test_the_ratings_table_comes_in_halves_with_a_column_per_ship():
    places = [(f"{w}-{n}", f"Level {w}-{n}") for w in range(1, 9) for n in range(1, 7)]
    table = {"vanguard": [Rating("1-1", "Level 1-1", 90.0, 1.9, 0.5)], "juggernaut": []}
    columns = rating_columns(places, ["vanguard", "juggernaut"], table)
    assert len(columns) == 2 * 3  # names, then the two ships, for each half
    assert columns[0][:2] == ["LEVEL", "1-1  Level 1-1"]
    assert columns[1][:3] == ["VANGU", "90", ""]  # rated, not yet
    assert len(columns[3]) == 1 + ROWS_PER_COLUMN and columns[3][1] == "5-1  Level 5-1"


def test_the_rating_title_says_what_is_going_on():
    assert "start AI learning first" in rating_title([], 10, "", "", None)
    assert "over 10 runs" in rating_title(["vanguard"], 10, "Rating VANGUARD: 3/48 ratings", "", None)
    assert rating_title(["vanguard"], 10, "", "saved/ratings.json", None).endswith("Saved to saved/ratings.json")
