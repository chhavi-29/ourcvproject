# main.py
# The main game loop — ties everything together
# Member 1 — owned by you

import pygame
import sys
import random

# Import our own modules
from game_objects import Blade, Fruit, Bomb, SlicedFruit, Explosion, SplashEffect
from game_engine  import ClassicMode, SurvivalMode

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

    # ── Game State ────────────────────────────────────────
    game_mode   = ClassicMode()
    blade       = Blade()
    all_sprites = pygame.sprite.Group()
    fruits      = pygame.sprite.Group()
    shake_timer = 0

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
                    game_mode   = ClassicMode()
                    blade       = Blade()
                    all_sprites.empty()
                    fruits.empty()
                    shake_timer = 0

        # ── Input (mouse for now, Member 2 replaces this) ─
        mx, my   = pygame.mouse.get_pos()
        velocity = 200  # mouse always has enough velocity

        # ── Update (only if game is still running) ────────
        if not game_mode.game_over:
            blade.update(mx, my)

            # Spawn fruits and bombs randomly
            if random.randint(1, 40) == 1:
                spawn_x = random.randint(100, WIDTH - 100)
                if random.randint(1, 5) == 1:
                    obj = Bomb(spawn_x, HEIGHT + 20, WIDTH, HEIGHT)
                else:
                    obj = Fruit(spawn_x, HEIGHT + 20, WIDTH, HEIGHT)
                all_sprites.add(obj)
                fruits.add(obj)

            all_sprites.update()

            # Survival mode timer
            if isinstance(game_mode, SurvivalMode):
                game_mode.update_timer(dt)

            # ── Collision Detection ───────────────────────
            segments = blade.get_segments()
            if velocity > MIN_CUT_VELOCITY and segments:
                for entity in list(fruits):
                    if entity.check_slice(segments):
                        if isinstance(entity, Bomb):
                            boom = Explosion(entity.pos_x, entity.pos_y)
                            all_sprites.add(boom)
                            entity.kill()
                            game_mode.on_bomb()
                            shake_timer = 20
                        else:
                            game_mode.on_slice(entity)
                            splash = SplashEffect(entity.pos_x, entity.pos_y,
                                                  entity.fruit_type, velocity)
                            h1 = SlicedFruit(entity.pos_x, entity.pos_y,
                                             entity.fruit_type, 1)
                            h2 = SlicedFruit(entity.pos_x, entity.pos_y,
                                             entity.fruit_type, 2)
                            all_sprites.add(splash, h1, h2)
                            entity.kill()

            # ── Check missed fruits ───────────────────────
            for entity in list(fruits):
                if entity.rect.top > HEIGHT:
                    if not isinstance(entity, Bomb):
                        game_mode.on_miss()
                    entity.kill()

        # ── Draw ─────────────────────────────────────────
        screen.blit(bg_img, (shake_x, shake_y))
        all_sprites.draw(screen)
        blade.draw(screen)

        # ── HUD ───────────────────────────────────────────
        hud  = font_small.render(game_mode.get_status(), True, WHITE)
        screen.blit(hud, (20, 20))
        hint = font_small.render("[ ESC to quit ]", True, (150, 150, 150))
        screen.blit(hint, (WIDTH - hint.get_width() - 20, 20))

        # ── Game Over Screen ──────────────────────────────
        if game_mode.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            over_txt    = font_big.render("GAME OVER", True, (255, 50, 50))
            score_txt   = font_med.render(f"Final Score: {game_mode.score}", True, WHITE)
            restart_txt = font_small.render(
                "Press R to restart  |  ESC to quit", True, (150, 150, 150))

            screen.blit(over_txt,    (WIDTH//2 - over_txt.get_width()//2,    200))
            screen.blit(score_txt,   (WIDTH//2 - score_txt.get_width()//2,   280))
            screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, 340))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ── Entry point ───────────────────────────────────────────
if __name__ == "__main__":
    main()