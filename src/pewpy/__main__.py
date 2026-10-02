"""Run the game (`make run`), reporting a crash."""

from pewpy import crash
from pewpy.app import main

if __name__ == "__main__":
    crash.run(main)
