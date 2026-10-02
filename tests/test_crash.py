import importlib
import runpy
import sys
import threading
from pathlib import Path
from typing import Any, cast

import pytest

from pewpy import app as app_module
from pewpy import crash


def inner(depth: int) -> None:
    marker = "a local variable"  # noqa: F841 - shown in the report
    if depth == 0:
        msg = "deep down"
        raise ValueError(msg)
    inner(depth - 1)


def chained() -> None:
    try:
        inner(2)
    except ValueError as error:
        msg = "while updating the world"
        raise RuntimeError(msg) from error


def caught() -> BaseException:
    try:
        chained()
    except RuntimeError as error:
        return error
    raise AssertionError  # pragma: no cover


@pytest.fixture
def state_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(crash.sys, "platform", "linux")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return tmp_path / "pewpy"


def test_the_stack_trace_has_every_frame_and_the_cause() -> None:
    trace = crash.stack_trace(caught())
    assert trace.count("in inner") == 3
    assert "ValueError: deep down" in trace
    assert "direct cause" in trace
    assert "RuntimeError: while updating the world" in trace


def test_the_report_adds_the_versions_and_the_local_variables() -> None:
    text = crash.report(caught())
    assert "pewpy crash" in text
    assert "Panda3D" in text
    assert "Python" in text
    assert "marker = 'a local variable'" in text
    assert "RuntimeError: while updating the world" in text


def test_long_values_are_cut_in_the_report() -> None:
    def explode() -> None:
        huge = "x" * 5000  # noqa: F841 - shown, cut
        raise ValueError

    try:
        explode()
    except ValueError as error:
        text = crash.report(error)
    assert max(len(line) for line in text.splitlines()) <= crash.MAX_LOCAL + 3


def test_a_crash_prints_the_trace_and_writes_the_log(state_folder: Path, capsys: pytest.CaptureFixture[str]) -> None:
    crash.handle(caught())
    err = capsys.readouterr().err
    assert "pewpy crashed" in err
    assert "ValueError: deep down" in err
    log = state_folder / crash.LOG_NAME
    assert str(log) in err
    assert "marker = 'a local variable'" in log.read_text()


def test_run_reports_a_crash_and_exits_with_an_error(
    state_folder: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    exits = []
    monkeypatch.setattr(crash.os, "_exit", exits.append)
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)  # put back after the test
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    crash.run(chained)
    assert exits == [1]
    assert "RuntimeError: while updating the world" in capsys.readouterr().err
    assert (state_folder / crash.LOG_NAME).is_file()


def test_run_lets_a_normal_exit_through(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)

    def leave() -> None:
        raise SystemExit(0)

    with pytest.raises(SystemExit):
        crash.run(leave)


def test_a_crash_in_a_thread_is_reported_with_its_name(
    state_folder: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    crash.install()
    worker = threading.Thread(target=chained, name="songs")
    worker.start()
    worker.join()
    err = capsys.readouterr().err
    assert "pewpy crashed in thread 'songs'" in err
    assert "Thread: songs" in (state_folder / crash.LOG_NAME).read_text()


def test_the_log_goes_to_the_users_folders(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(crash.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert crash.crash_log() == tmp_path / "pewpy" / "crash.log"


def test_the_log_without_a_state_folder_set_or_a_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(crash.sys, "platform", "linux")
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setattr(crash.Path, "home", lambda: tmp_path)
    assert crash.crash_log() == tmp_path / ".local" / "state" / "pewpy" / crash.LOG_NAME

    def homeless() -> crash.Path:
        raise RuntimeError

    monkeypatch.setattr(crash.Path, "home", homeless)
    assert crash.crash_log() is None
    assert crash.write_report(caught()) is None


def test_a_log_that_cant_be_written_is_skipped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    blocked = tmp_path / "a file, not a folder"
    blocked.write_text("")
    monkeypatch.setattr(crash.sys, "platform", "linux")
    monkeypatch.setenv("XDG_STATE_HOME", str(blocked))
    crash.handle(caught())
    err = capsys.readouterr().err
    assert "pewpy crashed" in err
    assert "Full report" not in err


def test_an_error_reported_twice_is_printed_once(state_folder: Path, capsys: pytest.CaptureFixture[str]) -> None:
    error = caught()
    crash.handle(error)
    capsys.readouterr()
    crash.handle(error)  # Panda3D passes it on after printing it through the hook
    assert capsys.readouterr().err == ""
    assert (state_folder / crash.LOG_NAME).is_file()


@pytest.mark.usefixtures("state_folder")
def test_the_hooks_report_crashes_but_not_ctrl_c_or_exits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    passed_on = []
    monkeypatch.setattr(crash.sys, "__excepthook__", lambda *args: passed_on.append(args[0]))
    crash._excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
    assert passed_on == [KeyboardInterrupt]
    error = ValueError("in the game loop")
    crash._excepthook(ValueError, error, None)
    assert "ValueError: in the game loop" in capsys.readouterr().err

    class Args:
        exc_type = SystemExit
        exc_value = SystemExit(0)
        exc_traceback = None
        thread = None

    crash._thread_excepthook(cast("Any", Args()))  # a stand-in for threading's
    assert capsys.readouterr().err == ""


def test_native_crashes_print_every_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    enabled = []
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    monkeypatch.setattr(crash.faulthandler, "is_enabled", lambda: False)
    monkeypatch.setattr(crash.faulthandler, "enable", lambda **kwargs: enabled.append(kwargs["all_threads"]))
    crash.install()
    assert enabled == [True]


def test_python_dash_m_pewpy_runs_the_game_reporting_crashes(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = []
    monkeypatch.setattr(crash, "run", ran.append)
    runpy.run_module("pewpy", run_name="__main__")
    assert ran == [app_module.main]
    import pewpy.__main__  # noqa: PLC0415 - after run_module, which warns if it was imported before

    ran.clear()
    importlib.reload(pewpy.__main__)  # imported, not run: the game doesn't start
    assert ran == []
