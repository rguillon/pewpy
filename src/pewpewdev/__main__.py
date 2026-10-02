import multiprocessing

from pewpewdev.app import main
from pewpy import crash

if __name__ == "__main__":  # not in the AI's worker processes, which start by importing this module again
    multiprocessing.freeze_support()
    crash.run(main)
