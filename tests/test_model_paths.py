from pathlib import Path

import pytest

from pewpy import data
from pewpy.data import model_folder, model_path


def test_a_model_is_found_in_its_group() -> None:
    assert model_folder("drone") == "enemies"
    assert model_folder("player") == "player"
    assert model_folder("capsule") == "items"
    assert model_path("drone").is_file()
    assert Path(str(model_path("drone"))).parent.name == "enemies"


def test_a_name_with_its_folder_is_where_it_says() -> None:
    assert model_folder("candidates/bosses/007_a") == "candidates/bosses"
    assert str(model_path("candidates/bosses/007_a")).endswith("models/candidates/bosses/007_a.json")


def test_a_model_in_no_group_is_right_in_models(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "models" / "bosses").mkdir(parents=True)
    (tmp_path / "models" / "bosses" / "big.json").write_text("{}")
    monkeypatch.setattr(data, "data_folder", lambda: tmp_path)
    assert model_path("big") == tmp_path / "models" / "bosses" / "big.json"
    assert model_path("loose") == tmp_path / "models" / "loose.json"
