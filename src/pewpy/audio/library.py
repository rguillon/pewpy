"""The songs, rendered from their MIDI files to WAV in a background thread, and kept on disk. No Panda3D.

Rendering a song takes a few seconds (see synth/), so it's done once: the WAV goes in a cache folder (the user's
cache, see `cache_folder`), named after what it was made from (the MIDI file, the synthesizer's version), so a
changed song is rendered again.
"""

import hashlib
import os
import sys
import threading
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING

from pewpy.audio import midi, synth

if TYPE_CHECKING:
    from pewpy.data import Traversable

SYNTH_VERSION = 1  # raise it when the synthesizer changes how songs sound: the cached ones are rendered again


def cache_folder() -> Path | None:
    """Where rendered songs are kept: the user's cache folder (None if there's no home to find it)."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        return Path(base) / "pewpy" / "music" if base else None
    base = os.environ.get("XDG_CACHE_HOME")
    if not base:
        try:
            base = str(Path.home() / ".cache")
        except RuntimeError:  # no home folder
            return None
    return Path(base) / "pewpy" / "music"


def render_wav(data: bytes, loop: bool) -> bytes:
    return synth.wav_bytes(synth.render(midi.read(data), loop=loop))


class Library:
    """The songs in `folder` (name.mid), rendered on request, one at a time in a background thread."""

    def __init__(self, folder: "Traversable", cache: Path | None) -> None:
        self.folder = folder
        self.cache = cache
        self.ready: dict[tuple[str, bool], bytes] = {}
        self.failed: set[str] = set()
        self._queue: deque[tuple[str, bool]] = deque()
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._thread: threading.Thread | None = None

    def names(self) -> list[str]:
        if not self.folder.is_dir():
            return []
        return sorted(entry.name[:-4] for entry in self.folder.iterdir() if entry.name.endswith(".mid"))

    def has(self, name: str) -> bool:
        return self.folder.joinpath(f"{name}.mid").is_file()

    def _cache_path(self, data: bytes, name: str, loop: bool) -> Path | None:
        if self.cache is None:
            return None
        digest = hashlib.sha1(data + f"{SYNTH_VERSION} {synth.RATE} {loop}".encode()).hexdigest()[:16]  # noqa: S324
        return self.cache / f"{name}-{digest}.wav"

    def wav(self, name: str, loop: bool = True) -> bytes:
        """The song as a WAV file, from the cache or rendered now (and cached)."""
        data = self.folder.joinpath(f"{name}.mid").read_bytes()
        path = self._cache_path(data, name, loop)
        if path is not None and path.is_file():
            return path.read_bytes()
        wav = render_wav(data, loop)
        if path is not None:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                for old in path.parent.glob(f"{name}-*.wav"):  # what an older version of the song left
                    old.unlink()
                path.write_bytes(wav)
            except OSError:
                pass  # no cache: rendered again next time
        return wav

    def cached(self, name: str, loop: bool = True) -> Path | None:
        """The song's WAV file in the cache, if it's there (each version of a song has its own file: a file is never
        rewritten while something may be reading it).
        """
        try:
            data = self.folder.joinpath(f"{name}.mid").read_bytes()
        except OSError:
            return None
        path = self._cache_path(data, name, loop)
        return path if path is not None and path.is_file() else None

    def request(self, name: str, loop: bool = True, first: bool = True) -> None:
        """Render `name` in the background (before the others waiting, if `first`); see `take`."""
        key = (name, loop)
        with self._lock:
            if key in self.ready or name in self.failed or not self.has(name):
                return
            if key in self._queue:
                self._queue.remove(key)
            if first:
                self._queue.appendleft(key)
            else:
                self._queue.append(key)
        self._start()
        self._wake.set()

    def take(self, name: str, loop: bool = True) -> bytes | None:
        """The rendered song if it's ready (else None, and it's requested)."""
        with self._lock:
            wav = self.ready.get((name, loop))
        if wav is None:
            self.request(name, loop)
        return wav

    def forget(self, name: str, loop: bool = True) -> None:
        """Let go of a rendered song once it's been taken (it's cached on disk: quick to get again)."""
        with self._lock:
            self.ready.pop((name, loop), None)

    def _start(self) -> None:
        if self._thread is None:
            self._thread = threading.Thread(target=self._work, name="songs", daemon=True)
            self._thread.start()

    def _work(self) -> None:
        while True:
            self._wake.wait()
            with self._lock:
                if not self._queue:
                    self._wake.clear()
                    continue
                name, loop = self._queue.popleft()
            try:
                wav = self.wav(name, loop)
            except (OSError, ValueError):
                with self._lock:
                    self.failed.add(name)
                continue
            with self._lock:
                self.ready[name, loop] = wav

    def wait(self, timeout: float = 60.0) -> bool:
        """Until nothing is waiting to be rendered (for tests and tools); False if it timed out."""
        deadline = threading.Event()
        for _ in range(int(timeout * 20)):
            with self._lock:
                busy = bool(self._queue) or (self._thread is not None and self._wake.is_set())
            if not busy:
                return True
            deadline.wait(0.05)
        return False
