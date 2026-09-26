"""
AudioManager: loads and plays sound effects and background music.

Audio hardware isn't guaranteed to be available on every machine (some
Linux setups, CI environments, etc. have none), so every operation here is
wrapped defensively — if sound can't be initialized or a file can't be
loaded/played, the game keeps running silently rather than crashing.
"""

import pygame

import settings


class AudioManager:
    def __init__(self):
        self.enabled = True
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except pygame.error as e:
            print(f"[audio] Could not initialize sound: {e}. Continuing without audio.")
            self.enabled = False

        self.sfx = {}
        # Each named sfx gets its own dedicated Channel (see _load_sfx). We
        # always play through that channel rather than the generic
        # Sound.play(), so a new catch_good retriggers cleanly instead of
        # stacking on top of whatever copies of it are still ringing out —
        # see play_sfx() for why that matters.
        self._sfx_channels = {}

        self._music_tracks = {
            "menu": settings.SOUNDS_DIR / "menu_music.ogg",
            "gameplay": settings.SOUNDS_DIR / "gameplay_music.ogg",
        }
        self._current_music = None

        # Independent on/off switches the pause menu toggles. Separate from
        # `enabled`, which reflects whether audio hardware is even present.
        self.sfx_enabled = True
        self.music_enabled = True

        # State for the delayed "game over -> sting -> menu music" sequence.
        # See trigger_game_over_sequence() / update().
        self._pending_game_over_timer = None   # seconds left before the sting plays, or None
        self._game_over_channel = None         # Channel the sting is playing on
        self._waiting_for_game_over_to_finish = False

        if self.enabled:
            self._load_sfx()

    def _load_sfx(self):
        sfx_files = {
            "catch_good": "catch_good.wav",
            "catch_bad": "catch_bad.wav",
            "game_over": "game_over.wav",
            "button_click": "button_click.wav",
        }

        # A plain Sound.play() grabs a free channel from a shared pool, so
        # during a catch flurry (e.g. high difficulty, several catches per
        # second) many overlapping copies of the same sound end up mixed
        # together — their waveforms add up and clip, which is the
        # "distorted" sound at high traffic. Giving each sfx name its own
        # reserved channel fixes this: playing on a channel that's already
        # playing something immediately replaces it instead of layering on
        # top, so you always hear one clean instance of a sound at a time,
        # no matter how fast catches come in.
        pygame.mixer.set_num_channels(max(pygame.mixer.get_num_channels(), 16))
        pygame.mixer.set_reserved(len(sfx_files))

        for index, (name, filename) in enumerate(sfx_files.items()):
            try:
                sound = pygame.mixer.Sound(str(settings.SOUNDS_DIR / filename))
                sound.set_volume(settings.SFX_VOLUME)
                self.sfx[name] = sound
                self._sfx_channels[name] = pygame.mixer.Channel(index)
            except pygame.error as e:
                print(f"[audio] Could not load {filename}: {e}")

    def play_sfx(self, name):
        if not self.enabled or not self.sfx_enabled:
            return
        sound = self.sfx.get(name)
        if sound is None:
            return
        channel = self._sfx_channels.get(name)
        if channel is not None:
            channel.play(sound)  # replaces whatever this channel was playing, no stacking
        else:
            sound.play()  # fallback, shouldn't normally happen

    def toggle_sfx(self):
        """Flips sound-effect playback on/off. Returns the new state."""
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled

    def toggle_music(self):
        """
        Flips music playback on/off. Returns the new state.

        Stops/resumes actual audio immediately, but keeps _current_music
        pointing at the logical track the rest of the game thinks is
        playing (e.g. "gameplay"), so turning music back on resumes the
        right track instantly rather than waiting for the next state-driven
        play_music() call.
        """
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            if self._current_music is not None:
                self._start_music_playback(self._current_music)
        else:
            pygame.mixer.music.stop()
        return self.music_enabled

    def play_music(self, track):
        """
        track: 'menu' or 'gameplay'. No-ops if that track is already the
        logical current track. Silently remembers the track without making
        sound if music is currently muted — toggle_music() will start it
        audibly the moment it's unmuted.

        Also cancels any in-progress game-over sequence (delayed sting, or
        waiting for the sting to finish before starting menu music) — an
        explicit switch means something else (e.g. a restart) has decided
        what should be playing now, so a stale sting shouldn't fire late or
        fight with it.
        """
        if not self.enabled:
            return

        self._pending_game_over_timer = None
        if self._waiting_for_game_over_to_finish and self._game_over_channel is not None:
            self._game_over_channel.stop()
        self._waiting_for_game_over_to_finish = False

        if self._current_music == track:
            return
        self._current_music = track
        if self.music_enabled:
            self._start_music_playback(track)

    def _start_music_playback(self, track):
        path = self._music_tracks.get(track)
        if path is None:
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            print(f"[audio] Could not play music '{track}': {e}")

    def stop_music(self):
        if not self.enabled or self._current_music is None:
            return
        pygame.mixer.music.stop()
        self._current_music = None

    def trigger_game_over_sequence(self, delay=None):
        """
        Call once, right when the game ends: stops whatever music was
        playing immediately, waits `delay` seconds in silence, plays the
        game-over sting, then starts the menu music loop once the sting
        finishes. Requires update(dt) to be called every frame to advance.
        """
        if not self.enabled:
            return
        if delay is None:
            delay = settings.GAME_OVER_SOUND_DELAY

        self.stop_music()
        self._pending_game_over_timer = delay
        self._game_over_channel = None
        self._waiting_for_game_over_to_finish = False

    def update(self, dt):
        """Call once per frame to advance the delayed game-over sequence."""
        if not self.enabled:
            return

        if self._pending_game_over_timer is not None:
            self._pending_game_over_timer -= dt
            if self._pending_game_over_timer <= 0:
                self._pending_game_over_timer = None
                if self.sfx_enabled:
                    sound = self.sfx.get("game_over")
                    channel = self._sfx_channels.get("game_over")
                    if sound and channel:
                        channel.play(sound)
                        self._game_over_channel = channel
                        self._waiting_for_game_over_to_finish = True
                    elif sound:
                        self._game_over_channel = sound.play()
                        self._waiting_for_game_over_to_finish = True
                    else:
                        # No sting loaded — just go straight to menu music.
                        self.play_music("menu")
                else:
                    # SFX muted: nothing to wait for, skip straight to menu music.
                    self.play_music("menu")

        elif self._waiting_for_game_over_to_finish:
            if self._game_over_channel is None or not self._game_over_channel.get_busy():
                self._waiting_for_game_over_to_finish = False
                self.play_music("menu")
