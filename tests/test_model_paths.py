from pathlib import Path

import pytest

from pewpy import data
from pewpy.data import model_folder, model_path, read_model
from pewpy.graphics import models


def test_a_model_is_found_in_its_group() -> None:
    assert model_folder("drone") == "enemies"
    assert model_folder("player") == "player"
    assert model_folder("capsule") == "items"
    assert model_path("drone").is_file()
    assert Path(str(model_path("drone"))).parent.name == "enemies"


def test_a_name_with_its_folder_is_where_it_says() -> None:
    assert model_folder("candidates/bosses/007") == "candidates/bosses"
    assert str(model_path("candidates/bosses/007")).endswith("models/candidates/bosses/007.json")


def test_a_part_is_drawn_in_its_models_file() -> None:
    assert model_folder("rockbreaker:drill") == "bosses"
    assert model_path("rockbreaker:drill") == model_path("rockbreaker")
    model, _ = read_model("rockbreaker")
    part, source = read_model("rockbreaker:drill")
    assert part == model["parts"]["drill"]
    assert source == "rockbreaker.json: part drill"
    assert model_folder("candidates/bosses/007:a") == "candidates/bosses"


def test_a_part_missing_from_its_models_file_is_an_error() -> None:
    with pytest.raises(ValueError, match="no part 'lost'"):
        read_model("rockbreaker:lost")
    with pytest.raises(ValueError, match="no part 'lost'"):
        read_model("drone:lost")  # a model without parts
    with pytest.raises(models.VoxelDrawingError, match="no part 'lost'"):
        models.load_voxels("rockbreaker:lost")


def test_a_model_in_no_group_is_right_in_models(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "models" / "bosses").mkdir(parents=True)
    (tmp_path / "models" / "bosses" / "big.json").write_text("{}")
    monkeypatch.setattr(data, "data_folder", lambda: tmp_path)
    assert model_path("big") == tmp_path / "models" / "bosses" / "big.json"
    assert model_path("loose") == tmp_path / "models" / "loose.json"
