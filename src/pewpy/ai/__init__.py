"""An AI that learns to play by itself (see 07-ai.md), without Panda3D.

sensors.py turns the world into what the AI sees, brain.py is its neural network, pilot.py flies the ship with it,
episode.py plays a level with a pilot, evolution.py and learning.py train the brains (one per ship) by evolution
strategies, rating.py rates every level for every ship from how the trained AI fares, files.py keeps the brains
and the ratings in the user's data folder.
"""
