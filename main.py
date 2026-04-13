# main.py
# The main game loop — ties everything together
# Member 1 — owned by you

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

input_manager = InputManager()

# ── Config ───────────────────────────────────────────────
WIDTH, HEIGHT    = 800, 600
FPS              = 60
MIN_CUT_VELOCITY = 150

# ── Colors ───────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Ninja CV")
    pygame.mouse.set_visible(False)  # Hide the system cursor
    clock  = pygame.time.Clock()

    # ── Load Background (temporary — Member 3 will replace this) ──
    try:
        bg_raw = pygame.image.load("assets/background/game_background.jpg").convert()
        bg_img = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
        dark   = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(80)
        dark.fill(BLACK)
        bg_img.blit(dark, (0, 0))
    except:
        bg_img = pygame.Surface((WIDTH, HEIGHT))
        bg_img.fill((30, 30, 30))

    # ── Fonts ─────────────────────────────────────────────
    font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    font_med   = pygame.font.SysFont("Arial", 32)
    font_small = pygame.font.SysFont("Arial", 24)
    font_question = pygame.font.SysFont("Arial", 40, bold=True)

    # ── Game State ────────────────────────────────────────
    game_mode   = EduMode()
    blade       = Blade()
    all_sprites = pygame.sprite.Group()
    answers     = pygame.sprite.Group()
    shake_timer = 0

    question_gen = QuestionGenerator()
    current_question, correct_answer, wrong_answers = question_gen.generate(game_mode.difficulty)
    state = "WAITING"
    spawn_timer = 0
    transition_msg = ""

    last_mx, last_my = pygame.mouse.get_pos()

    # ── Game Loop ─────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS)

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Restart on R key when game over
                if event.key == pygame.K_r and game_mode.game_over:
                    game_mode   = EduMode()
                    blade       = Blade()
                    all_sprites.empty()
                    answers.empty()
                    shake_timer = 0
                    current_question, correct_answer, wrong_answers = question_gen.generate(game_mode.difficulty)
                    state = "WAITING"
                    spawn_timer = 0
                    transition_msg = ""
                    last_mx, last_my = pygame.mouse.get_pos()

        # ── Input (mouse for now, Member 2 replaces this) ─
        input_data = input_manager.get_input()
        if input_data["active"]:
            mx, my   = input_data["x"], input_data["y"]
            velocity = input_data["velocity"]
        else:
            mx, my   = pygame.mouse.get_pos()  # fallback to mouse if no hand detected
            velocity = 200

        # ── Update (only if game is still running) ────────
        if not game_mode.game_over:
            blade.update(mx, my)

            # Game states
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

                # ── Collision Detection ───────────────────────
                segments = blade.get_segments()
                if velocity > MIN_CUT_VELOCITY and segments:
                    for entity in list(answers):
                        if entity.check_slice(segments):
                            if isinstance(entity, AnswerFruit):
                                game_mode.on_correct_slice()
                                splash = SplashEffect(entity.pos_x, entity.pos_y, "orange", velocity)
                                h1 = SlicedFruit(entity.pos_x, entity.pos_y, "orange", 1)
                                h2 = SlicedFruit(entity.pos_x, entity.pos_y, "orange", 2)
                                all_sprites.add(splash, h1, h2)
                                
                                for f in list(answers):
                                    f.kill()
                                transition_msg = "Awesome!"
                                spawn_timer = 0
                                state = "TRANSITION"
                                break
                            elif isinstance(entity, AnswerBomb):
                                game_mode.on_wrong_slice()
                                boom = Explosion(entity.pos_x, entity.pos_y)
                                all_sprites.add(boom)
                                shake_timer = 20
                                for f in list(answers):
                                    f.kill()
                                transition_msg = "Wrong!"
                                spawn_timer = 0
                                state = "TRANSITION"
                                break

                # ── Check missed fruits ───────────────────────
                if state == "PLAYING":
                    for entity in list(answers):
                        if entity.rect.top > HEIGHT:
                            if isinstance(entity, AnswerFruit):
                                game_mode.on_missed()
                                for f in list(answers):
                                    f.kill()
                                transition_msg = "Oops! Missed it!"
                                spawn_timer = 0
                                state = "TRANSITION"
                            else:
                                entity.kill()

            elif state == "TRANSITION":
                all_sprites.update()
                max_timer = 120 if "Awesome" in transition_msg else 160
                spawn_timer += 1
                if spawn_timer > max_timer:
                    current_question, correct_answer, wrong_answers = question_gen.generate(game_mode.difficulty)
                    spawn_timer = 0
                    state = "WAITING"

        # ── Draw ─────────────────────────────────────────
        screen.blit(bg_img, (shake_x, shake_y))
        all_sprites.draw(screen)
        blade.draw(screen)

        if state in ("WAITING", "PLAYING") and not game_mode.game_over:
            q_text = font_question.render(current_question, True, WHITE)
            screen.blit(q_text, (WIDTH//2 - q_text.get_width()//2, 30))

        if state == "TRANSITION" and not game_mode.game_over:
            color = (50, 255, 50) if "Awesome" in transition_msg else (255, 50, 50)
            trans_txt = font_big.render(transition_msg, True, color)
            screen.blit(trans_txt, (WIDTH//2 - trans_txt.get_width()//2, HEIGHT//2))

        # ── HUD ───────────────────────────────────────────
        hud  = font_small.render(game_mode.get_status(), True, WHITE)
        screen.blit(hud, (20, 20))
        hint = font_small.render("[ ESC to quit ]", True, (150, 150, 150))
        screen.blit(hint, (WIDTH - hint.get_width() - 20, 20))

        # CV Debug Overlay
        cam_status = "Cam OK" if input_data["frame"] is not None else "Cam ERROR"
        hand_status = "Hand ACTIVE" if input_data["active"] else "No Hand"
        debug_txt = font_small.render(f"{cam_status} | {hand_status}", True, (255, 255, 0))
        screen.blit(debug_txt, (20, 60))

        if input_data["frame"] is not None:
            # Display small webcam preview in corner
            preview = cv2.resize(input_data["frame"], (160, 120))
            preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            preview_surface = pygame.surfarray.make_surface(np.swapaxes(preview_rgb, 0, 1))
            screen.blit(preview_surface, (WIDTH - 180, HEIGHT - 140))
            
        for i in range(game_mode.lives):
            pygame.draw.circle(screen, (255, 0, 0), (WIDTH-50-i*40, 30), 10)

        # ── Game Over Screen ──────────────────────────────
        if game_mode.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            perf = game_mode.get_performance_report()
            over_txt    = font_big.render("GAME OVER", True, (255, 50, 50))
            score_txt   = font_med.render(f"Final Score: {perf['score']} | Accuracy: {perf['accuracy']}%", True, WHITE)
            stats_txt   = font_small.render(f"Correct: {perf['correct']} | Wrong: {perf['wrong']}", True, WHITE)
            restart_txt = font_small.render(
                "Press R to restart  |  ESC to quit", True, (150, 150, 150))

            screen.blit(over_txt,    (WIDTH//2 - over_txt.get_width()//2,    200))
            screen.blit(score_txt,   (WIDTH//2 - score_txt.get_width()//2,   280))
            screen.blit(stats_txt,   (WIDTH//2 - stats_txt.get_width()//2,   320))
            screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, 380))

        pygame.display.flip()

    input_manager.stop()
    pygame.quit()
    sys.exit()

# ── Entry point ───────────────────────────────────────────
if __name__ == "__main__":
    main()