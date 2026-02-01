from pathlib import Path

import pygame


class SoundManager:
    def __init__(self, sound_dir: Path):
        self.sound_dir = sound_dir

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        self.sfx_swing = self._load_sound("weapon_swing01.wav")
        self.sfx_damage = self._load_sound("receivedamage.wav")
        self.sfx_hitmonster = self._load_sound("hitmonster.wav")
        self.sfx_gameover = self._load_sound("gameover1.wav")
        self.sfx_pickup = self._load_sound("pickupitem0.wav")
        self.sfx_treasure = self._load_sound("treasure1.wav")
        self.sfx_door = self._load_sound("undoor1.wav")
        self.sfx_fanfare = self._load_sound("fanfare.wav")

    def _load_sound(self, name: str):
        path = self.sound_dir / name
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    def play_music(self):
        path = self.sound_dir / "BlueBoyAdventure.wav"
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def play_cave_music(self):
        path = self.sound_dir / "Dungeon.wav"
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def play_swing(self):
        if self.sfx_swing is not None:
            try:
                self.sfx_swing.play()
            except Exception:
                pass

    def play_damage(self):
        if self.sfx_damage is not None:
            try:
                self.sfx_damage.play()
            except Exception:
                pass

    def play_hitmonster(self):
        if self.sfx_hitmonster is not None:
            try:
                self.sfx_hitmonster.play()
            except Exception:
                pass

    def play_gameover(self):
        if self.sfx_gameover is not None:
            try:
                self.sfx_gameover.play()
            except Exception:
                pass

    def play_pickup(self):
        if self.sfx_pickup is not None:
            try:
                self.sfx_pickup.play()
            except Exception:
                pass

    def play_treasure(self):
        if self.sfx_treasure is not None:
            try:
                self.sfx_treasure.play()
            except Exception:
                pass

    def play_door(self):
        if self.sfx_door is not None:
            try:
                self.sfx_door.play()
            except Exception:
                pass

    def play_fanfare(self):
        if self.sfx_fanfare is not None:
            try:
                self.sfx_fanfare.play()
            except Exception:
                pass