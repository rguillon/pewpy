import sys
import threading

import pytest

from pewpy import crash


def inner(depth: int) -> None:
    marker = "a local variable"  # noqa: F841 - shown in the report
    if depth == 0:
        raise ValueError("deep down")  # noqa: TRY003 - a test's message
    inner(depth - 1)


def chained() -> None:
    try:
        inner(2)
    except ValueError as error:
        raise RuntimeError("while updating the world") from error  # noqa: TRY003 - a test's message


def caught() -> BaseException:
    try:
        chained()
    except RuntimeError as error:
        return error
    raise AssertionError  # pragma: no cover


@pytest.fixture
def state_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(crash.sys, "platform", "linux")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return tmp_path / "pewpy"


def test_the_stack_trace_has_every_frame_and_the_cause():
    trace = crash.stack_trace(caught())
    assert trace.count("in inner") == 3
    assert "ValueError: deep down" in trace
    assert "direct cause" in trace
    assert "RuntimeError: while updating the world" in trace


def test_the_report_adds_the_versions_and_the_local_variables():
    text = crash.report(caught())
    assert "pewpy crash" in text and "Panda3D" in text and "Python" in text
    assert "marker = 'a local variable'" in text
    assert "RuntimeError: while updating the world" in text


def test_long_values_are_cut_in_the_report():
    def explode() -> None:
        huge = "x" * 5000  # noqa: F841 - shown, cut
        raise ValueError

    try:
        explode()
    except ValueError as error:
        text = crash.report(error)
    assert max(len(line) for line in text.splitlines()) <= crash.MAX_LOCAL + 3


def test_a_crash_prints_the_trace_and_writes_the_log(state_folder, capsys):
    crash.handle(caught())
    err = capsys.readouterr().err
    assert "pewpy crashed" in err and "ValueError: deep down" in err
    log = state_folder / crash.LOG_NAME
    assert str(log) in err
    assert "marker = 'a local variable'" in log.read_text()


def test_run_reports_a_crash_and_exits_with_an_error(state_folder, monkeypatch, capsys):
    exits = []
    monkeypatch.setattr(crash.os, "_exit", exits.append)
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)  # put back after the test
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    crash.run(chained)
    assert exits == [1]
    assert "RuntimeError: while updating the world" in capsys.readouterr().err
    assert (state_folder / crash.LOG_NAME).is_file()


def test_run_lets_a_normal_exit_through(monkeypatch):
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)

    def leave() -> None:
        raise SystemExit(0)

    with pytest.raises(SystemExit):
        crash.run(leave)


def test_a_crash_in_a_thread_is_reported_with_its_name(state_folder, monkeypatch, capsys):
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    crash.install()
    worker = threading.Thread(target=chained, name="songs")
    worker.start()
    worker.join()
    err = capsys.readouterr().err
    assert "pewpy crashed in thread 'songs'" in err
    assert "Thread: songs" in (state_folder / crash.LOG_NAME).read_text()


def test_the_log_goes_to_the_users_folders(monkeypatch, tmp_path):
    monkeypatch.setattr(crash.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert crash.crash_log() == tmp_path / "pewpy" / "crash.log"
