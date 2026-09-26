"""
Scoreboard: tracks score and lives for the current run, and persists a
high score to disk between runs.
"""

import json

import settings


class Scoreboard:
    def __init__(self):
        self.score = 0
        self.lives = settings.STARTING_LIVES
        self.high_score = self._load_high_score()

    def add_score(self, points):
        self.score += points

    def lose_life(self):
        self.lives -= 1

    @property
    def is_game_over(self):
        return self.lives <= 0

    def _load_high_score(self):
        try:
            with open(settings.HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
            return data.get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            # Missing or corrupt file shouldn't crash the game — just start
            # from zero, same as a first-ever run.
            return 0

    def save_high_score_if_needed(self):
        """Call when a run ends. Returns True if this run set a new high score."""
        if self.score > self.high_score:
            self.high_score = self.score
            with open(settings.HIGHSCORE_FILE, "w") as f:
                json.dump({"high_score": self.high_score}, f)
            return True
        return False
