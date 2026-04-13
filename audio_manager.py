import pygame
import os

class AudioManager:
    def __init__(self):
        # We need pygame mixer initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.sounds = {}
        self.music_loaded = False

        # Define paths
        base_path = os.path.join("assets", "audio")
        
        # Load Sound Effects
        try:
            self.sounds['correct'] = pygame.mixer.Sound(os.path.join(base_path, "Fruit Splat Score 01 Sound Effect 056561276 Nw Prev.wav"))
            self.sounds['incorrect'] = pygame.mixer.Sound(os.path.join(base_path, "bomb explosion sound.wav"))
            self.sounds['level_up'] = pygame.mixer.Sound(os.path.join(base_path, "game sound fast.mp3"))
            self.sounds['game_over'] = pygame.mixer.Sound(os.path.join(base_path, "36. U I Game Over.mp3"))
            
            # Lower volumes slightly
            for sound in self.sounds.values():
                sound.set_volume(0.6)
        except Exception as e:
            print(f"Warning: Failed to load some sound effects: {e}")

        # Try to load background music
        try:
            pygame.mixer.music.load(os.path.join(base_path, "34. Music Menu.mp3"))
            pygame.mixer.music.set_volume(0.3)
            self.music_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load background music: {e}")

    def play_background_music(self):
        if self.music_loaded:
            pygame.mixer.music.play(-1) # -1 means loop indefinitely

    def stop_background_music(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def play_correct_chime(self):
        if 'correct' in self.sounds:
            self.sounds['correct'].play()

    def play_wrong_buzz(self):
        if 'incorrect' in self.sounds:
            self.sounds['incorrect'].play()

    def play_level_up(self):
        if 'level_up' in self.sounds:
            self.sounds['level_up'].play()
            
    def play_game_over(self):
        if 'game_over' in self.sounds:
            self.sounds['game_over'].play()
