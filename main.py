# main.py
# The main game loop — ties everything together
# Member 1 — owned by you, UI/Audio by Member 3

import pygame
import sys
import random
import cv2
import numpy as np

# Import our own modules
from game_objects import (Blade, AnswerFruit, AnswerBomb, SlicedFruit, Explosion, SplashEffect)
from game_engine import EduMode
from question_generator import QuestionGenerator
from input_manager import InputManager
from ui_manager import UIManager
from audio_manager import AudioManager

# ── Config ───────────────────────────────────────────────
WIDTH, HEIGHT    = 800, 600
FPS              = 60
MIN_CUT_VELOCITY = 150

# ── Colors ───────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)

def blur_surf(surface, amt):
    """Utility to blur a Pygame surface using cv2"""
    if amt < 1: return surface
    scale = 1.0 / float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tiny Thinkers - CV Edition")
    pygame.mouse.set_visible(False)
    clock  = pygame.time.Clock()

    input_manager = InputManager()
    ui_manager = UIManager(WIDTH, HEIGHT)
    audio_manager = AudioManager()
    
    audio_manager.play_background_music()

    # ── Load Background ──
    try:
        bg_raw = pygame.image.load("assets/background/game_background.jpg").convert()
        bg_img = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
        # Dimming & Blurring for gameplay
        bg_img = blur_surf(bg_img, 4)
        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(100)
        dark.fill(BLACK)
        bg_img.blit(dark, (0, 0))
    except Exception as e:
        print("Bg not loaded:", e)
        bg_img = pygame.Surface((WIDTH, HEIGHT))
        bg_img.fill((30, 30, 30))

    # ── Fonts ─────────────────────────────────────────────
    font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)

    # ── Game State ────────────────────────────────────────
    game_mode   = EduMode()
    blade       = Blade()
    all_sprites = pygame.sprite.Group()
    answers     = pygame.sprite.Group()
    shake_timer = 0
    highest_score = 0

    question_gen = QuestionGenerator()
    current_question, correct_answer, wrong_answers = "", 0, []
    
    state = "SPLASH"
    spawn_timer = 0
    transition_msg = ""
    last_difficulty = game_mode.difficulty

    # ── Game Loop ─────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS)
        mouse_clicked = False

        # Screen shake
        shake_x, shake_y = 0, 0
        if shake_timer > 0:
            shake_timer -= 1
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)

        # ── Events ───────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ── Input ────────────────────────────────────────
        input_data = input_manager.get_input()
        if input_data["active"]:
            mx, my   = input_data["x"], input_data["y"]
            velocity = input_data["velocity"]
        else:
            mx, my   = pygame.mouse.get_pos()
            velocity = 200

        blade.update(mx, my)
        sliced_ui = False
        if velocity > MIN_CUT_VELOCITY and blade.get_segments():
            sliced_ui = True

        # ── State Machine ─────────────────────────────────
        if state == "SPLASH":
            ui_manager.draw_splash_screen(screen)
            blade.draw(screen)
            
            # Check interaction
            if mouse_clicked or (sliced_ui and ui_manager.start_btn_rect.collidepoint(mx, my)):
                state = "WAITING"
                current_question, correct_answer, wrong_answers = question_gen.generate(game_mode.difficulty)
                
        elif state in ("WAITING", "PLAYING", "TRANSITION"):
            # Update Score tracking
            if game_mode.score > highest_score:
                highest_score = game_mode.score
                
            # Level up check
            if game_mode.difficulty != last_difficulty:
                audio_manager.play_level_up()
                ui_manager.trigger_level_up_animation()
                last_difficulty = game_mode.difficulty

            if state == "WAITING":
                spawn_timer += 1
                if spawn_timer > 120:
                    pos = [150, 300, 500, 650]
                    random.shuffle(pos)
                    fruit = AnswerFruit(pos[0], HEIGHT+20, WIDTH, HEIGHT, correct_answer)
                    all_sprites.add(fruit)
                    answers.add(fruit)
                    for i, w in enumerate(wrong_answers):
                        bomb = AnswerBomb(pos[i+1], HEIGHT+20, WIDTH, HEIGHT, w)
                        all_sprites.add(bomb)
                        answers.add(bomb)
                    spawn_timer = 0
                    state = "PLAYING"
            
            elif state == "PLAYING":
                all_sprites.update()
                segments = blade.get_segments()
                if velocity > MIN_CUT_VELOCITY and segments:
                    for entity in list(answers):
                        if entity.check_slice(segments):
                            if isinstance(entity, AnswerFruit):
                                game_mode.on_correct_slice()
                                audio_manager.play_correct_chime()
                                splash = SplashEffect(entity.pos_x, entity.pos_y, "orange", velocity)
                                h1 = SlicedFruit(entity.pos_x, entity.pos_y, "orange", 1)
                                h2 = SlicedFruit(entity.pos_x, entity.pos_y, "orange", 2)
                                all_sprites.add(splash, h1, h2)
                                for f in list(answers): f.kill()
                                transition_msg = "Awesome!"
                                spawn_timer = 0
                                state = "TRANSITION"
                                break
                            elif isinstance(entity, AnswerBomb):
                                game_mode.on_wrong_slice()
                                audio_manager.play_wrong_buzz()
                                boom = Explosion(entity.pos_x, entity.pos_y)
                                all_sprites.add(boom)
                                shake_timer = 20
                                for f in list(answers): f.kill()
                                transition_msg = "Wrong!"
                                spawn_timer = 0
                                state = "TRANSITION"
                                
                                if game_mode.game_over:
                                    audio_manager.play_game_over()
                                    # Will go to GAME_OVER after TRANSITION
                                break

                # Miss logic
                if state == "PLAYING":
                    for entity in list(answers):
                        if entity.rect.top > HEIGHT:
                            if isinstance(entity, AnswerFruit):
                                game_mode.on_missed()
                                audio_manager.play_wrong_buzz()
                                for f in list(answers): f.kill()
                                transition_msg = "Oops! Missed it!"
                                spawn_timer = 0
                                state = "TRANSITION"
                                if game_mode.game_over:
                                    audio_manager.play_game_over()
                                    # Will go to GAME_OVER after TRANSITION
                            else:
                                entity.kill()

            elif state == "TRANSITION":
                all_sprites.update()
                max_timer = 120 if "Awesome" in transition_msg else 160
                spawn_timer += 1
                if spawn_timer > max_timer:
                    if game_mode.game_over:
                        spawn_timer = 0
                        state = "GAME_OVER"
                    else:
                        current_question, correct_answer, wrong_answers = question_gen.generate(game_mode.difficulty)
                        spawn_timer = 0
                        state = "WAITING"

            # ── Drawing gameplay ──
            screen.blit(bg_img, (shake_x, shake_y))
            all_sprites.draw(screen)
            blade.draw(screen)
            
            # Use UIManager for HUD
            ui_manager.draw_hud(screen, game_mode.score, game_mode.lives, 3, current_question if state in ("WAITING", "PLAYING") else "")

            if state == "TRANSITION":
                color = (255, 255, 153) if "Awesome" in transition_msg else (255, 99, 71)
                trans_txt = font_big.render(transition_msg, True, color)
                # shadow
                shadow = font_big.render(transition_msg, True, BLACK)
                screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 2, HEIGHT//2 + 2))
                screen.blit(trans_txt, (WIDTH//2 - trans_txt.get_width()//2, HEIGHT//2))

        elif state == "GAME_OVER":
            spawn_timer += 1
            screen.blit(bg_img, (shake_x, shake_y))
            blade.draw(screen)
            ui_manager.draw_game_over(screen, game_mode.get_performance_report(), highest_score)
            
            # Restart Check (cooldown of roughly 1.5 seconds to prevent accidental restart)
            if spawn_timer > 90:
                if mouse_clicked or (sliced_ui and ui_manager.restart_btn_rect.collidepoint(mx, my)):
                    # Reset
                    game_mode = EduMode()
                    last_difficulty = game_mode.difficulty
                    all_sprites.empty()
                    answers.empty()
                    shake_timer = 0
                    current_question, correct_answer, wrong_answers = "", 0, []
                    state = "SPLASH"

        # ── Common HUD/CV overlays ──
        if state != "SPLASH":
            hint = font_small.render("[ ESC to quit ]", True, (150, 150, 150))
            screen.blit(hint, (WIDTH - hint.get_width() - 20, HEIGHT - 30))

            cam_status = "Cam OK" if input_data["frame"] is not None else "Cam ERROR"
            hand_status = "Hand ACTIVE" if input_data["active"] else "No Hand"
            debug_txt = font_small.render(f"{cam_status} | {hand_status}", True, (255, 255, 0))
            screen.blit(debug_txt, (20, HEIGHT - 30))

            if input_data["frame"] is not None:
                preview = cv2.resize(input_data["frame"], (160, 120))
                preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
                # flip preview so it acts like a mirror
                preview_rgb = cv2.flip(preview_rgb, 1)
                preview_surface = pygame.surfarray.make_surface(np.swapaxes(preview_rgb, 0, 1))
                screen.blit(preview_surface, (WIDTH - 180, HEIGHT - 160))

        pygame.display.flip()

    input_manager.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()