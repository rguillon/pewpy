"""Run the game with the dev tools' screens (`make dev`)."""

import multiprocessing

from pewpy import crash
from pewpy.tools.dev.app import main

if __name__ == "__main__":  # not in the AI's worker processes, which start by importing this module again
    multiprocessing.freeze_support()
    crash.run(main)
