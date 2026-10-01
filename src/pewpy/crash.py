"""Crash reports, to debug a crash after the fact.

`run(main)` runs the game so that if it crashes:
- on an uncaught Python exception (in the game loop, an event handler, or a background thread): the full stack trace
  (with the exceptions it was raised from) is printed on stderr, and a fuller report is written to the crash log
  (`crash_log()`: the same trace plus the local variables of every frame, the time, the versions, the platform);
  then the game leaves with exit code 1;
- on a native crash (a segmentation fault in Panda3D or the graphics driver): Python's faulthandler prints every
  thread's stack on stderr.

The packaged game has no console: its stderr goes to %LOCALAPPDATA%\\pewpy\\output.log (packaging/setup.py).
"""

import contextlib
import datetime
import faulthandler
import os
import platform
import sys
import threading
import traceback
from collections.abc import Callable
from pathlib import Path
from types import TracebackType

LOG_NAME = "crash.log"
MAX_LOCAL = 300  # characters of a local variable's value in the report


def log_folder() -> Path | None:
    """Where the crash log goes: the user's state folder (None if there's no home to find it)."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        return Path(base) / "pewpy" if base else None
    base = os.environ.get("XDG_STATE_HOME")
    if not base:
        try:
            base = str(Path.home() / ".local" / "state")
        except RuntimeError:  # no home folder
            return None
    return Path(base) / "pewpy"


def crash_log() -> Path | None:
    folder = log_folder()
    return folder / LOG_NAME if folder else None


def stack_trace(error: BaseException) -> str:
    """The full stack trace, as Python prints it: every frame, and the exceptions this one was raised from."""
    return "".join(traceback.format_exception(type(error), error, error.__traceback__))


def report(error: BaseException, thread: str = "") -> str:
    """The crash log's text: when and where, the versions, then the stack trace with every frame's local
    variables.
    """
    try:
        from panda3d.core import PandaSystem

        panda = PandaSystem.getVersionString()
    except ImportError:  # pragma: no cover - Panda3D is always there in the game
        panda = "?"
    header = [
        f"pewpy crash, {datetime.datetime.now().astimezone():%Y-%m-%d %H:%M:%S %z}",
        f"Python {sys.version.split()[0]}, Panda3D {panda}, {platform.platform()}",
        f"Thread: {thread or threading.current_thread().name}",
        f"Command: {' '.join(sys.argv)}",
        "",
    ]
    details = traceback.TracebackException.from_exception(error, capture_locals=True)
    lines = [_short_locals(line) for line in details.format()]
    return "\n".join(header) + "".join(lines)


def _short_locals(line: str) -> str:
    """Cut long values of local variables (a frame's "name = value" lines), so the report stays readable."""
    parts = []
    for part in line.splitlines(keepends=True):
        if len(part) > MAX_LOCAL and " = " in part:
            part = part[:MAX_LOCAL] + "...\n"
        parts.append(part)
    return "".join(parts)


def write_report(error: BaseException, thread: str = "") -> Path | None:
    """Write the crash log; where it went (None if it couldn't be written)."""
    path = crash_log()
    if path is None:
        return None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report(error, thread), encoding="utf-8")
    except Exception:
        return None
    return path


_reported: list[BaseException] = []  # the last error reported, so it isn't printed twice


def handle(error: BaseException, thread: str = "") -> None:
    """Print the stack trace on stderr and write the crash log. Panda3D prints a task's exception (through the
    exception hook) before passing it on: the second time, only the log is written again, with the frames it went
    through since.
    """
    if _reported and _reported[0] is error:
        write_report(error, thread)
        return
    _reported[:] = [error]
    where = f" in thread {thread!r}" if thread else ""
    sys.stderr.write(f"\n*** pewpy crashed{where} ***\n{stack_trace(error)}")
    path = write_report(error, thread)
    if path is not None:
        sys.stderr.write(f"Full report (with every frame's local variables): {path}\n")
    sys.stderr.flush()


def _excepthook(kind: type[BaseException], error: BaseException, tb: TracebackType | None) -> None:
    if issubclass(kind, KeyboardInterrupt):
        sys.__excepthook__(kind, error, tb)
        return
    handle(error.with_traceback(tb))


def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
    if args.exc_value is None or issubclass(args.exc_type, SystemExit):
        return
    handle(args.exc_value.with_traceback(args.exc_traceback), args.thread.name if args.thread else "")


def install() -> None:
    """Report crashes from now on: uncaught exceptions (any thread), native crashes (faulthandler)."""
    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook
    if sys.stderr is not None and not faulthandler.is_enabled():
        with contextlib.suppress(AttributeError, ValueError, OSError):  # a stderr without a file descriptor
            faulthandler.enable(file=sys.stderr, all_threads=True)


def run(main: Callable[[], None]) -> None:
    """Run the game, reporting a crash. A crash leaves at once with exit code 1: under WSL the graphics driver can
    hang while the window is torn down (see app.py, finalizeExit).
    """
    install()
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as error:
        handle(error)
        os._exit(1)
