"""Менеджер звукових ефектів та біомної фонової музики для Galaxy Defender."""

import os
from kivy.core.audio import SoundLoader
from game.storage import (
    is_sound_enabled,
    set_sound_enabled,
    is_music_enabled,
    set_music_enabled,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT_DIR, "assets", "audio")
USER_AUDIO_DIR = os.path.join(ROOT_DIR, "звуки")


class AudioManager:
    """Централізоване керування всіма звуками та фоновою музикою різних рівнів."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._sound_cache = {}
        self._bgm_tracks = {}
        self._current_bgm = None
        self._current_biome = "space"
        self._bgm_playing = False
        self._load_sounds()

    @property
    def current_bgm_track(self) -> str:
        """Повертає ідентифікатор активного біомного музичного треку."""
        return self._current_biome

    def load_sounds(self):
        """Публічний метод перезавантаження аудіо."""
        self._load_sounds()

    def _load_sounds(self):
        """Попередньо завантажує звукові файли та біомні саундтреки."""
        # 1. Ефекти з assets/audio
        sound_names = [
            "laser",
            "beam",
            "charge",
            "plasma",
            "explosion",
            "boss_explosion",
            "hit",
            "shield",
            "upgrade",
            "warning",
            "game_over",
            "burn",
            "freeze",
            "shock",
            "splash",
            "warp",
        ]
        for name in sound_names:
            path = os.path.join(AUDIO_DIR, f"{name}.wav")
            if os.path.exists(path):
                try:
                    sound = SoundLoader.load(path)
                    if sound:
                        self._sound_cache[name] = sound
                except Exception:
                    pass

        # 2. Перевірка користувацьких ассетів з папки "звуки"
        if os.path.exists(USER_AUDIO_DIR):
            try:
                # Користувацький постріл лазера
                user_laser_path = os.path.join(
                    USER_AUDIO_DIR, "zvuk-vystrela-iz-lazera_[Pro-Sound.org].mp3"
                )
                if os.path.exists(user_laser_path):
                    user_laser = SoundLoader.load(user_laser_path)
                    if user_laser:
                        self._sound_cache["laser_user"] = user_laser
                        # Використовуємо його також для laser
                        self._sound_cache["laser"] = user_laser

                # Користувацька космічна музика
                user_space_bgm = os.path.join(
                    USER_AUDIO_DIR, "kulakovka-space-283176.mp3"
                )
                if os.path.exists(user_space_bgm):
                    sound = SoundLoader.load(user_space_bgm)
                    if sound:
                        sound.loop = True
                        sound.volume = 0.50
                        self._bgm_tracks["space"] = sound
            except Exception:
                pass

        # 3. Біомні музичні треки з assets/audio
        biome_bgm_files = {
            "space": "bgm.wav",
            "lava": "bgm_lava.wav",
            "water": "bgm_water.wav",
            "cyber_storm": "bgm_cyber.wav",
            "ice": "bgm_ice.wav",
        }
        for biome_id, fname in biome_bgm_files.items():
            if biome_id in self._bgm_tracks:
                continue  # Вже завантажено користувацький трек
            path = os.path.join(AUDIO_DIR, fname)
            if os.path.exists(path):
                try:
                    s = SoundLoader.load(path)
                    if s:
                        s.loop = True
                        s.volume = 0.50
                        self._bgm_tracks[biome_id] = s
                except Exception:
                    pass

        # Встановлюємо стартовий трек
        self._current_bgm = self._bgm_tracks.get("space")

    def play(self, name: str, volume: float = 1.0):
        """Відтворює звуковий ефект."""
        if not is_sound_enabled():
            return
        sound = self._sound_cache.get(name)
        if sound:
            try:
                sound.volume = max(0.0, min(1.0, volume))
                sound.play()
            except Exception:
                pass

    def play_biome_music(self, biome_id: str):
        """Безшовно перемикає фонову музику на саундтрек відповідного біому/рівня."""
        self._current_biome = biome_id
        new_track = self._bgm_tracks.get(biome_id) or self._bgm_tracks.get("space")

        if not is_music_enabled():
            self._current_bgm = new_track
            return

        if self._current_bgm == new_track and self._bgm_playing:
            return

        # Зупиняємо попередній трек
        if self._current_bgm and self._bgm_playing:
            try:
                self._current_bgm.stop()
            except Exception:
                pass
            self._bgm_playing = False

        self._current_bgm = new_track
        if self._current_bgm:
            try:
                self._current_bgm.loop = True
                self._current_bgm.volume = 0.50
                self._current_bgm.play()
                self._bgm_playing = True
            except Exception:
                pass

    def start_music(self):
        """Запускає фонову музику для поточного біому."""
        if not is_music_enabled():
            return
        track = self._current_bgm or self._bgm_tracks.get(self._current_biome) or self._bgm_tracks.get("space")
        if track and not self._bgm_playing:
            try:
                track.loop = True
                track.volume = 0.50
                track.play()
                self._current_bgm = track
                self._bgm_playing = True
            except Exception:
                pass

    def stop_music(self):
        """Зупиняє фонову музику."""
        if self._current_bgm and self._bgm_playing:
            try:
                self._current_bgm.stop()
            except Exception:
                pass
            self._bgm_playing = False

    def pause_music(self):
        """Призупиняє музику (під час паузи гри)."""
        if self._current_bgm and self._bgm_playing:
            try:
                self._current_bgm.stop()
            except Exception:
                pass

    def resume_music(self):
        """Відновлює музику."""
        if is_music_enabled() and self._current_bgm and self._bgm_playing:
            try:
                self._current_bgm.play()
            except Exception:
                pass

    def toggle_sound(self) -> bool:
        new_val = not is_sound_enabled()
        set_sound_enabled(new_val)
        return new_val

    def toggle_music(self) -> bool:
        new_val = not is_music_enabled()
        set_music_enabled(new_val)
        if new_val:
            self.start_music()
        else:
            self.stop_music()
        return new_val


def get_audio_manager() -> AudioManager:
    return AudioManager.get_instance()
