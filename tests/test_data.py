from pathlib import Path

from pewpy import data


def test_the_data_files_are_in_the_package():
    assert data.data_folder().joinpath("levels").is_dir()


def test_a_packaged_game_has_them_next_to_its_executable(monkeypatch, tmp_path):
    monkeypatch.setattr(data.sys, "frozen", True, raising=False)
    monkeypatch.setattr(data.sys, "executable", str(tmp_path / "pewpy.exe"))
    assert data.data_folder() == Path(tmp_path) / "pewpy"
