"""The sounds and the music: songs rendered in the background, the music following the game."""

from pewpy.app.keys import MUSIC_KEY, Keys
from pewpy.audio.cues import music
from pewpy.audio.library import Library, cache_folder
from pewpy.audio.sound import Audio
from pewpy.data import data_folder
from pewpy.game.states import State


class Sound(Keys):
    """The audio, and the music each screen plays."""

    def _setup_audio(self) -> None:
        library = Library(data_folder() / "music", cache_folder())
        manager = self.sfxManagerList[0] if self.sfxManagerList else None
        self.audio = Audio(self.loader, manager, self.musicManager, library)
        # Rendered in the background in the order they're likely needed (once: they're kept on disk).
        library.request("title", first=False)
        for index in range(len(self.worlds)):
            library.request(f"world_{index + 1}", first=False)
        library.request("boss", first=False)
        library.request("level_complete", loop=False, first=False)
        library.request("game_over", loop=False, first=False)
        self.accept(MUSIC_KEY, self.audio.toggle_music)

    def _update_audio(self, dt: float) -> None:
        world, state = self.world, self.states.state
        self.audio.set_laser(world is not None and state is State.PLAYING and world.laser is not None)
        boss = world is not None and (world.boss is not None or world.boss_beaten)
        self.audio.set_music(music(state, self.places[self.level_index][0], boss), quiet=state is State.PAUSED)
        self.audio.update(dt)
