import importlib
import runpy

import pytest

from pewpy import app as app_module
from pewpy import crash


def test_python_dash_m_pewpy_runs_the_game_reporting_crashes(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = []
    monkeypatch.setattr(crash, "run", ran.append)
    runpy.run_module("pewpy", run_name="__main__")
    assert ran == [app_module.main]
    import pewpy.__main__  # noqa: PLC0415 - after run_module, which warns if it was imported before

    ran.clear()
    importlib.reload(pewpy.__main__)  # imported, not run: the game doesn't start
    assert ran == []
