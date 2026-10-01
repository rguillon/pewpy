import multiprocessing

from pewpy import crash
from pewpy.app import main

if __name__ == "__main__":  # not in the AI's worker processes, which start by importing this module again
    multiprocessing.freeze_support()  # the packaged game's worker processes start here
    crash.run(main)
