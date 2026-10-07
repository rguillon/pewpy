"""Making the game's data: its models, songs, backgrounds, levels, the AI's brain, and the README's screenshots.

One subpackage per kind of data, each with what makes it and, for the Dev menu, its browser (independent from
rendering, the app shows it): models/ (the player's ships', the enemies' and the bosses' models, and the final bosses
from their plans), music/ (the songs, composed as MIDI), backgrounds/ (background candidates from themes), levels/
(the levels from the worlds' plans, `make levels`), ai_training/ (teaching the AI player, `make learn`),
compact_json/ (how the enemies' and bosses' JSON is written), screenshots.py (the README's screenshots, from the Dev
menu) and paths.py (where the command line tools write).
"""
