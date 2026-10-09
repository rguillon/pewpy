"""Ships assembled in 3D from the catalog of built-in parts (models/parts/): the player's, the enemies', the bosses'.

They're all made the same way, only their size differs; a boss also has destroyable parts. placing.py picks parts for
the size wanted and places them where they fit, modules.py assembles a boss's destroyable parts, ship.py holds the
cubes and writes the 3D drawing (a boss's parts apart), paint.py paints the bits, selection.py makes and finishes a
ship.
"""
