from pathlib import Path

import pytest

from pewpy import data
from pewpy.data import model_folder, model_path, read_model
from pewpy.graphics import models
from pewpy.graphics.models.drawings.files import read_drawing


def test_a_model_is_found_in_its_group() -> None:
    assert model_folder("drone") == "enemies"
    assert model_folder("player") == "player"
    assert model_folder("capsule") == "items"
    assert model_path("drone").is_file()
    assert Path(str(model_path("drone"))).parent.name == "enemies"


def test_a_part_is_drawn_in_its_models_file() -> None:
    model, _ = read_model("avalanche")
    name = next(iter(model["parts"]))  # whatever its parts are (the Dev menu remakes them)
    assert model_folder(f"avalanche:{name}") == "bosses"
    assert model_path(f"avalanche:{name}") == model_path("avalanche")
    part, source = read_model(f"avalanche:{name}")
    assert part == model["parts"][name]
    assert source == f"avalanche.json: part {name}"


def test_a_part_missing_from_its_models_file_is_an_error() -> None:
    with pytest.raises(ValueError, match="no part 'lost'"):
        read_model("avalanche:lost")
    with pytest.raises(ValueError, match="no part 'lost'"):
        read_model("drone:lost")  # a model without parts
    with pytest.raises(models.VoxelDrawingError, match="no part 'lost'"):
        read_drawing("avalanche:lost")


def test_a_model_in_no_group_is_right_in_models(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "models" / "bosses").mkdir(parents=True)
    (tmp_path / "models" / "bosses" / "big.json").write_text("{}")
    monkeypatch.setattr(data, "data_folder", lambda: tmp_path)
    assert model_path("big") == tmp_path / "models" / "bosses" / "big.json"
    assert model_path("loose") == tmp_path / "models" / "loose.json"
