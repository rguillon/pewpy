from pathlib import Path

import pytest

from pewpy import data


def test_the_data_files_are_at_the_top_of_the_project() -> None:
    assert data.data_folder() == data.SOURCE_DATA
    assert data.data_folder().joinpath("levels").is_dir()


def test_an_installed_wheel_has_them_in_the_package(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "data").mkdir()
    monkeypatch.setattr(data.resources, "files", lambda _package: tmp_path)
    assert data.data_folder() == tmp_path / "data"


def test_a_packaged_game_has_them_next_to_its_executable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(data.sys, "frozen", True, raising=False)
    monkeypatch.setattr(data.sys, "executable", str(tmp_path / "pewpy.exe"))
    assert data.data_folder() == Path(tmp_path) / "data"
