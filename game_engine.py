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

# ════════════════════════════════════════════════════════
# EDU MODE — learning math questions
# ════════════════════════════════════════════════════════
class EduMode:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.correct_count = 0
        self.wrong_count = 0
        self.questions_answered = 0
        self.difficulty = "easy"
        self.game_over = False

    def on_correct_slice(self):
        self.score += 10
        self.correct_count += 1
        self.questions_answered += 1
        if self.correct_count > 0 and self.correct_count % 5 == 0:
            self.level_up()

    def on_wrong_slice(self):
        self.score -= 5
        self.wrong_count += 1
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True

    def on_missed(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True

    def level_up(self):
        if self.difficulty == "easy":
            self.difficulty = "medium"
        elif self.difficulty == "medium":
            self.difficulty = "hard"

    def get_status(self):
        return f"Score: {self.score}    Level: {self.difficulty.capitalize()}"

    def get_performance_report(self):
        accuracy = 0
        total = self.correct_count + self.wrong_count
        if total > 0:
            accuracy = int((self.correct_count / total) * 100)
        return {
            "score": self.score,
            "correct": self.correct_count,
            "wrong": self.wrong_count,
            "accuracy": accuracy,
            "questions_answered": self.questions_answered
        }