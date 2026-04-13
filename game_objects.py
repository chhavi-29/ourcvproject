# game_objects.py
import pygame
import random
import time
import os
from collections import deque
import physics

# ── Colors ──────────────────────────────────────────────
RED    = (255, 50,  50)
GREEN  = (50,  255, 50)
WHITE  = (255, 255, 255)
ORANGE = (255, 165, 0)

# ════════════════════════════════════════════════════════
# BLADE  — the finger/mouse trail drawn on screen
# ════════════════════════════════════════════════════════
class Blade:
    def __init__(self):
        self.points    = deque(maxlen=20)
        self.color     = (0, 255, 255)
        self.min_width = 5
        self.max_width = 25

    def update(self, x, y):
        """Call every frame with current mouse/finger position."""
        now = time.time()
        self.points.append((x, y, now))

        # Remove points older than 0.15 seconds
        while self.points and now - self.points[0][2] > 0.15:
            self.points.popleft()

    def draw(self, screen):
        """Draw trail — thick at tip, thin at tail."""
        if len(self.points) < 2:
            return

        pts = list(self.points)
        for i in range(len(pts) - 1):
            p1, p2 = pts[i], pts[i + 1]

            ratio = i / len(pts)
            width = int(self.min_width + (self.max_width - self.min_width) * ratio)

            pygame.draw.line(screen, self.color,
                             (p1[0], p1[1]), (p2[0], p2[1]), width)
            pygame.draw.circle(screen, self.color, (p2[0], p2[1]), width // 2)

    def get_segments(self):
        """Returns blade as list of line segments for collision detection."""
        pts = list(self.points)
        return [
            ((pts[i][0], pts[i][1]), (pts[i+1][0], pts[i+1][1]))
            for i in range(len(pts) - 1)
        ]
    


    # ════════════════════════════════════════════════════════
# FRUIT — the objects the player slices
# ════════════════════════════════════════════════════════
class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, fruit_type=None):
        super().__init__()

        self.screen_w = width
        self.screen_h = height

        # Pick a random fruit type if none given
        types = ["apple", "banana", "coconut", "orange", "pineapple", "watermelon"]
        self.fruit_type = fruit_type if fruit_type else random.choice(types)

        # Load image
        try:
            path = f"assets/fruits/{self.fruit_type}_small.png"
            if not os.path.exists(path):
                path = f"assets/fruits/{self.fruit_type}.png"
            raw = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(raw, (70, 70))
        except:
            # Fallback: draw a colored circle if image missing
            self.image = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (35, 35), 35)

        self.rect = self.image.get_rect(center=(x, y))

        # Position as floats for smooth movement
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Physics — launched upward with random angle
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-18, -12)  # negative = upward

    def update(self):
        """Move the fruit using physics every frame."""
        self.pos_x, self.pos_y, self.vel_x, self.vel_y = physics.apply_physics(
            self.pos_x, self.pos_y, self.vel_x, self.vel_y
        )
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def check_slice(self, segments):
        """
        Check if the blade has sliced this fruit.
        Returns True if any blade segment hits the fruit circle.
        """
        cx, cy = self.rect.centerx, self.rect.centery
        radius = self.rect.width // 2

        for (x1, y1), (x2, y2) in segments:
            if physics.check_capsule_circle_collision(
                (x1, y1), (x2, y2),
                thickness=10,
                center=(cx, cy),
                radius=radius
            ):
                return True
        return False
    

    # ════════════════════════════════════════════════════════
# BOMB — player must AVOID slicing these
# ════════════════════════════════════════════════════════
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()

        self.screen_w = width
        self.screen_h = height

        # Load bomb image
        try:
            path = "assets/fruits/bomb_small.png"
            if not os.path.exists(path):
                path = "assets/fruits/bomb.png"
            raw = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(raw, (70, 70))
        except:
            # Fallback: dark circle
            self.image = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (40, 40, 40), (35, 35), 35)
            pygame.draw.circle(self.image, RED, (35, 35), 35, 3)

        self.rect = self.image.get_rect(center=(x, y))

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-16, -10)

    def update(self):
        self.pos_x, self.pos_y, self.vel_x, self.vel_y = physics.apply_physics(
            self.pos_x, self.pos_y, self.vel_x, self.vel_y
        )
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def check_slice(self, segments):
        """Same slice check as Fruit — but hitting this loses points!"""
        cx, cy = self.rect.centerx, self.rect.centery
        radius = self.rect.width // 2

        for (x1, y1), (x2, y2) in segments:
            if physics.check_capsule_circle_collision(
                (x1, y1), (x2, y2),
                thickness=10,
                center=(cx, cy),
                radius=radius
            ):
                return True
        return False


# ════════════════════════════════════════════════════════
# SLICED FRUIT — the two halves after slicing
# ════════════════════════════════════════════════════════
class SlicedFruit(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit_type, half):
        super().__init__()

        # half = 1 or 2 (left half or right half)
        try:
            path = f"assets/fruits/{fruit_type}_half_{half}_small.png"
            if not os.path.exists(path):
                path = f"assets/fruits/{fruit_type}_half_{half}.png"
            raw = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(raw, (50, 50))
        except:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (25, 25), 25)

        self.rect  = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Two halves fly apart in opposite directions
        self.vel_x = random.uniform(-5, -2) if half == 1 else random.uniform(2, 5)
        self.vel_y = random.uniform(-8, -4)
        self.alpha = 255  # for fade out effect

    def update(self):
        self.pos_x, self.pos_y, self.vel_x, self.vel_y = physics.apply_physics(
            self.pos_x, self.pos_y, self.vel_x, self.vel_y
        )
        self.rect.center = (int(self.pos_x), int(self.pos_y))

        # Fade out gradually
        self.alpha = max(0, self.alpha - 4)
        self.image.set_alpha(self.alpha)

        # Remove when fully faded or off screen
        if self.alpha == 0 or self.rect.top > 700:
            self.kill()


# ════════════════════════════════════════════════════════
# EXPLOSION — shown when a bomb is sliced
# ════════════════════════════════════════════════════════
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        try:
            raw = pygame.image.load("assets/vfx/explosion_small.png").convert_alpha()
            self.image = pygame.transform.scale(raw, (120, 120))
        except:
            self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 0), (60, 60), 60)

        self.rect  = self.image.get_rect(center=(x, y))
        self.timer = 30  # lives for 30 frames then disappears

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()


# ════════════════════════════════════════════════════════
# SPLASH — coloured juice splash when fruit is sliced
# ════════════════════════════════════════════════════════
class SplashEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit_type, velocity):
        super().__init__()

        # Pick splash color based on fruit
        splash_map = {
            "watermelon": "splash_red",
            "orange":     "splash_orange",
            "banana":     "splash_yellow",
            "apple":      "splash_red",
            "pineapple":  "splash_yellow",
            "coconut":    "splash_transparent",
        }
        splash_name = splash_map.get(fruit_type, "splash_red")

        try:
            raw = pygame.image.load(f"assets/vfx/{splash_name}_small.png").convert_alpha()
            self.image = pygame.transform.scale(raw, (100, 100))
        except:
            self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (50, 50), 50)

        self.rect  = self.image.get_rect(center=(x, y))
        self.timer = 20  # disappears after 20 frames

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# ════════════════════════════════════════════════════════
# ANSWER FRUIT — correct math answer
# ════════════════════════════════════════════════════════
class AnswerFruit(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, number):
        super().__init__()
        self.screen_w = width
        self.screen_h = height
        self.number = number

        types = ["apple", "banana", "coconut", "orange", "pineapple", "watermelon"]
        self.fruit_type = random.choice(types)
        try:
            path = f"assets/fruits/{self.fruit_type}_small.png"
            if not os.path.exists(path):
                path = f"assets/fruits/{self.fruit_type}.png"
            raw = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(raw, (120, 120))
        except:
            self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (60, 60), 60)

        # Draw dark circle behind text for clarity
        bg = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(bg, (0, 0, 0, 180), (25, 25), 25)
        border_rect = bg.get_rect(center=(60, 60))
        self.image.blit(bg, border_rect)
        
        font = pygame.font.SysFont("Arial", 40, bold=True)
        text = font.render(str(number), True, WHITE)
        text_rect = text.get_rect(center=(60, 60))
        self.image.blit(text, text_rect)

        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.vel_x = random.uniform(-0.1, 0.1)
        self.vel_y = random.uniform(-4.8, -4.4)

    def update(self):
        self.pos_x, self.pos_y, self.vel_x, self.vel_y = physics.apply_physics(
            self.pos_x, self.pos_y, self.vel_x, self.vel_y
        )
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def check_slice(self, segments):
        cx, cy = self.rect.centerx, self.rect.centery
        radius = self.rect.width // 2
        for (x1, y1), (x2, y2) in segments:
            if physics.check_capsule_circle_collision(
                (x1, y1), (x2, y2), thickness=10, center=(cx, cy), radius=radius
            ):
                return True
        return False

# ════════════════════════════════════════════════════════
# ANSWER BOMB — incorrect math answer
# ════════════════════════════════════════════════════════
class AnswerBomb(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, number):
        super().__init__()
        self.screen_w = width
        self.screen_h = height
        self.number = number

        types = ["apple", "banana", "coconut", "orange", "pineapple", "watermelon"]
        self.fruit_type = random.choice(types)
        try:
            path = f"assets/fruits/{self.fruit_type}_small.png"
            if not os.path.exists(path):
                path = f"assets/fruits/{self.fruit_type}.png"
            raw = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(raw, (120, 120))
        except:
            self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (60, 60), 60)

        # Draw dark circle behind text for clarity
        bg = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(bg, (0, 0, 0, 180), (25, 25), 25)
        border_rect = bg.get_rect(center=(60, 60))
        self.image.blit(bg, border_rect)
        
        font = pygame.font.SysFont("Arial", 40, bold=True)
        text = font.render(str(number), True, WHITE)
        text_rect = text.get_rect(center=(60, 60))
        self.image.blit(text, text_rect)

        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.vel_x = random.uniform(-0.1, 0.1)
        self.vel_y = random.uniform(-4.8, -4.4)

    def update(self):
        self.pos_x, self.pos_y, self.vel_x, self.vel_y = physics.apply_physics(
            self.pos_x, self.pos_y, self.vel_x, self.vel_y
        )
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def check_slice(self, segments):
        cx, cy = self.rect.centerx, self.rect.centery
        radius = self.rect.width // 2
        for (x1, y1), (x2, y2) in segments:
            if physics.check_capsule_circle_collision(
                (x1, y1), (x2, y2), thickness=10, center=(cx, cy), radius=radius
            ):
                return True
        return False