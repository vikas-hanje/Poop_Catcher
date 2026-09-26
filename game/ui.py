"""
HUD rendering: score text and life icons, drawn every frame during play.
"""

import pygame

import settings
from game.asset_utils import load_scaled_sprite


class HUD:
    def __init__(self):
        font_path = settings.FONTS_DIR / "Fredoka-Bold.ttf"
        self.score_font = pygame.font.Font(str(font_path), 48)
        self.high_score_font = pygame.font.Font(str(font_path), 30)

        self.life_icon = load_scaled_sprite(
            settings.IMAGES_DIR / "life_icon.png", settings.LIFE_ICON_SIZE
        )

    def draw(self, surface, scoreboard):
        score_surf = self.score_font.render(
            f"Score: {scoreboard.score}", True, settings.WHITE
        )
        surface.blit(score_surf, (30, 24))

        high_score_surf = self.high_score_font.render(
            f"High Score: {scoreboard.high_score}", True, settings.GOLD
        )
        # Directly below the score line, small gap between the two.
        surface.blit(high_score_surf, (30, 24 + score_surf.get_height() + 4))

        # Lives drawn as a row of icons, right-aligned.
        icon_w, icon_h = settings.LIFE_ICON_SIZE
        spacing = 10
        lives_to_draw = max(scoreboard.lives, 0)
        start_x = settings.SCREEN_WIDTH - 30 - (icon_w + spacing) * lives_to_draw
        for i in range(lives_to_draw):
            x = start_x + i * (icon_w + spacing)
            surface.blit(self.life_icon, (x, 30))
