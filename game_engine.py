# game_engine.py
# Handles game modes, score, lives and game over condition
# Member 1 — owned by you

# ════════════════════════════════════════════════════════
# CLASSIC MODE — 3 lives, lose a life for each missed fruit
# ════════════════════════════════════════════════════════
class ClassicMode:
    def __init__(self):
        self.score     = 0
        self.lives     = 3
        self.game_over = False

    def on_slice(self, entity):
        """Called when a fruit is sliced. Adds 1 point."""
        self.score += 1

    def on_miss(self):
        """Called when a fruit falls off screen without being sliced."""
        self.lives -= 1
        if self.lives <= 0:
            self.lives     = 0
            self.game_over = True

    def on_bomb(self):
        """Called when a bomb is sliced. Deducts 5 points."""
        self.score -= 5
        if self.score < 0:
            self.score = 0

    def get_status(self):
        """Returns a string shown on screen during gameplay."""
        return f"Score: {self.score}    Lives: {self.lives}"


# ════════════════════════════════════════════════════════
# SURVIVAL MODE — no lives, score as much as possible in 60 seconds
# ════════════════════════════════════════════════════════
class SurvivalMode:
    def __init__(self):
        self.score     = 0
        self.time_left = 60       # seconds
        self.game_over = False
        self._ms_left  = 60000   # milliseconds for precise countdown

    def on_slice(self, entity):
        """Each slice gives 1 point."""
        self.score += 1

    def on_miss(self):
        """Missing a fruit does nothing in survival mode."""
        pass

    def on_bomb(self):
        """Hitting a bomb deducts 5 points."""
        self.score -= 5
        if self.score < 0:
            self.score = 0

    def update_timer(self, dt_ms):
        """
        Call this every frame with milliseconds elapsed since last frame.
        dt_ms comes from pygame clock.tick()
        """
        self._ms_left -= dt_ms
        self.time_left = max(0, self._ms_left // 1000)
        if self._ms_left <= 0:
            self.game_over = True

    def get_status(self):
        return f"Score: {self.score}    Time: {self.time_left}s"