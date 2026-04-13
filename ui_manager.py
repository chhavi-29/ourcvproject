import pygame
import math

class UIManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Colors (Pastel theme from balloon arch)
        self.COLOR_PINK = (255, 182, 193)
        self.COLOR_BLUE = (173, 216, 230)
        self.COLOR_YELLOW = (255, 255, 153)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_RED = (255, 99, 71)
        
        # Load Fonts
        try:
            # Tries to get Comic Sans or falls back to SysFont
            self.font_title = pygame.font.SysFont("Comic Sans MS", 72, bold=True)
            self.font_btn = pygame.font.SysFont("Comic Sans MS", 48, bold=True)
            self.font_instructions = pygame.font.SysFont("Comic Sans MS", 28)
            
            # Keep numbers in a clean sans-serif like Arial
            self.font_hud = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_question = pygame.font.SysFont("Arial", 44, bold=True)
        except Exception:
            self.font_title = pygame.font.Font(None, 72)
            self.font_btn = pygame.font.Font(None, 48)
            self.font_instructions = pygame.font.Font(None, 28)
            self.font_hud = pygame.font.Font(None, 36)
            self.font_question = pygame.font.Font(None, 44)
            
        # Create Heart Surface for Lives and Score
        self.heart_surface = self._create_heart_surface(40, self.COLOR_PINK)
        self.heart_score_surface = self._create_heart_surface(30, self.COLOR_PINK)
        
        # State variables
        self.level_up_timer = 0
        self.start_btn_rect = pygame.Rect(self.width//2 - 125, self.height//2 + 50, 250, 80)
        self.restart_btn_rect = pygame.Rect(self.width//2 - 150, self.height//2 + 150, 300, 80)

    def _create_heart_surface(self, size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # Simple geometric heart: two circles and a polygon
        r = size // 4
        # Left circle
        pygame.draw.circle(surface, color, (r, r), r)
        # Right circle
        pygame.draw.circle(surface, color, (size - r, r), r)
        # Triangle
        pygame.draw.polygon(surface, color, [
            (0, r+2), 
            (size, r+2), 
            (size//2, size)
        ])
        # Outline for visibility
        pygame.draw.circle(surface, self.COLOR_WHITE, (r, r), r, 2)
        pygame.draw.circle(surface, self.COLOR_WHITE, (size - r, r), r, 2)
        pygame.draw.polygon(surface, self.COLOR_WHITE, [(0, r+2), (size, r+2), (size//2, size)], 2)
        
        return surface

    def draw_splash_screen(self, screen):
        # Draw background base
        screen.fill(self.COLOR_BLUE)
        
        # Title "Tiny Thinkers"
        title_text = self.font_title.render("Tiny Thinkers", True, self.COLOR_YELLOW)
        # Shadow
        shadow = self.font_title.render("Tiny Thinkers", True, self.COLOR_BLACK)
        screen.blit(shadow, (self.width//2 - title_text.get_width()//2 + 4, 84))
        screen.blit(title_text, (self.width//2 - title_text.get_width()//2, 80))
        
        # Start Button
        pygame.draw.rect(screen, self.COLOR_PINK, self.start_btn_rect, border_radius=15)
        pygame.draw.rect(screen, self.COLOR_WHITE, self.start_btn_rect, width=4, border_radius=15)
        
        btn_text = self.font_btn.render("START", True, self.COLOR_WHITE)
        screen.blit(btn_text, (self.start_btn_rect.centerx - btn_text.get_width()//2, self.start_btn_rect.centery - btn_text.get_height()//2))
        
        # Instructions
        inst_text = self.font_instructions.render("Note: Use ONLY ONE HAND to slice the answers!", True, self.COLOR_WHITE)
        bg_rect = inst_text.get_rect(center=(self.width//2, self.height - 50))
        pygame.draw.rect(screen, self.COLOR_BLACK, bg_rect.inflate(20, 10))
        screen.blit(inst_text, bg_rect)

    def draw_hud(self, screen, score, lives, max_lives, current_question):
        # Top Left: Score (Heart Icon + Score)
        screen.blit(self.heart_score_surface, (20, 20))
        score_text = self.font_hud.render(str(score), True, self.COLOR_WHITE)
        screen.blit(score_text, (20 + self.heart_score_surface.get_width() + 10, 15))
        
        # Top Right: Lives (Row of Hearts)
        start_x = self.width - 20 - self.heart_surface.get_width()
        for i in range(max_lives):
            if i < lives:
                screen.blit(self.heart_surface, (start_x - (i * (self.heart_surface.get_width() + 10)), 15))
                
        # Top Center: Question
        if current_question:
            q_text = self.font_question.render(current_question, True, self.COLOR_YELLOW)
            # Outline
            q_outline = self.font_question.render(current_question, True, self.COLOR_BLACK)
            screen.blit(q_outline, (self.width//2 - q_text.get_width()//2 + 2, 22))
            screen.blit(q_text, (self.width//2 - q_text.get_width()//2, 20))
            
        # Draw basic level up animation if active
        if self.level_up_timer > 0:
            self._draw_level_up_animation(screen)
            self.level_up_timer -= 1

    def trigger_level_up_animation(self):
        # 60 frames roughly 1 second at 60fps
        self.level_up_timer = 60 

    def _draw_level_up_animation(self, screen):
        # A simple expanding text animation
        # The user can help modify this
        progress = self.level_up_timer / 60.0
        size_mult = 1.0 + (1.0 - progress) # expands from 1x to 2x
        
        try:
            anim_font = pygame.font.SysFont("Comic Sans MS", int(48 * size_mult), bold=True)
        except:
            anim_font = pygame.font.Font(None, int(48 * size_mult))
            
        text = anim_font.render("LEVEL UP!", True, self.COLOR_YELLOW)
        alpha_surface = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
        # Fade out
        alpha_surface.blit(text, (0, 0))
        alpha_surface.set_alpha(int(255 * progress))
        
        screen.blit(alpha_surface, (self.width//2 - text.get_width()//2, self.height//2 - text.get_height()//2 - 100))

    def draw_game_over(self, screen, performance, highest_score):
        # Dimming overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(self.COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # "GAME OVER"
        over_txt = self.font_title.render("GAME OVER", True, self.COLOR_RED)
        screen.blit(over_txt, (self.width//2 - over_txt.get_width()//2, 100))
        
        # Stats Background Box
        box_w, box_h = 450, 250
        box_rect = pygame.Rect(self.width//2 - box_w//2, 200, box_w, box_h)
        pygame.draw.rect(screen, self.COLOR_BLUE, box_rect, border_radius=20)
        pygame.draw.rect(screen, self.COLOR_WHITE, box_rect, width=5, border_radius=20)
        
        # Stats Text
        stat_color = self.COLOR_BLACK
        y_offset = 220
        high_score_txt = self.font_hud.render(f"Highest Score: {highest_score}", True, stat_color)
        score_txt = self.font_hud.render(f"Score: {performance['score']}", True, stat_color)
        accuracy_txt = self.font_instructions.render(f"Accuracy: {performance['accuracy']}%", True, stat_color)
        correct_txt = self.font_instructions.render(f"Total Correct: {performance['correct']}", True, stat_color)
        
        screen.blit(high_score_txt, (self.width//2 - high_score_txt.get_width()//2, y_offset))
        screen.blit(score_txt, (self.width//2 - score_txt.get_width()//2, y_offset + 50))
        screen.blit(accuracy_txt, (self.width//2 - accuracy_txt.get_width()//2, y_offset + 120))
        screen.blit(correct_txt, (self.width//2 - correct_txt.get_width()//2, y_offset + 170))
        
        # Restart Button
        pygame.draw.rect(screen, self.COLOR_YELLOW, self.restart_btn_rect, border_radius=15)
        pygame.draw.rect(screen, self.COLOR_WHITE, self.restart_btn_rect, width=4, border_radius=15)
        
        r_text = self.font_btn.render("Restart Game", True, self.COLOR_BLACK)
        screen.blit(r_text, (self.restart_btn_rect.centerx - r_text.get_width()//2, self.restart_btn_rect.centery - r_text.get_height()//2))
