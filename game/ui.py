"""
HUD rendering: score text and life icons, drawn every frame during play.

Both get a semi-transparent panel behind them plus a text drop-shadow,
since plain text/icons directly on the busy tiled background were hard to
read on their own.
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

    def _draw_panel(self, surface, rect, padding=12, radius=12, alpha=140):
        panel_rect = rect.inflate(padding * 2, padding * 2)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, alpha), panel.get_rect(), border_radius=radius)
        surface.blit(panel, panel_rect.topleft)

    def _draw_text_with_shadow(self, surface, font, text, color, pos, offset=2):
        shadow_surf = font.render(text, True, settings.BLACK)
        surface.blit(shadow_surf, (pos[0] + offset, pos[1] + offset))
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, pos)
        return text_surf

    def draw(self, surface, scoreboard):
        score_text = f"Score: {scoreboard.score}"
        high_score_text = f"High Score: {scoreboard.high_score}"

        # Measure first (render() is cheap) so the panel can be sized to
        # snugly fit both lines before anything is actually drawn.
        score_probe = self.score_font.render(score_text, True, settings.WHITE)
        high_score_probe = self.high_score_font.render(high_score_text, True, settings.GOLD)
        block_w = max(score_probe.get_width(), high_score_probe.get_width())
        block_h = score_probe.get_height() + 4 + high_score_probe.get_height()
        self._draw_panel(surface, pygame.Rect(30, 24, block_w, block_h))

        self._draw_text_with_shadow(surface, self.score_font, score_text, settings.WHITE, (30, 24))
        self._draw_text_with_shadow(
            surface, self.high_score_font, high_score_text, settings.GOLD,
            (30, 24 + score_probe.get_height() + 4),
        )

        # Lives drawn as a row of icons, right-aligned. Positions unchanged
        # from before — just adding a panel behind them.
        icon_w, icon_h = settings.LIFE_ICON_SIZE
        spacing = 10
        lives_to_draw = max(scoreboard.lives, 0)
        start_x = settings.SCREEN_WIDTH - 30 - (icon_w + spacing) * lives_to_draw

        if lives_to_draw > 0:
            row_w = (icon_w + spacing) * (lives_to_draw - 1) + icon_w
            self._draw_panel(surface, pygame.Rect(start_x, 30, row_w, icon_h))

        for i in range(lives_to_draw):
            x = start_x + i * (icon_w + spacing)
            surface.blit(self.life_icon, (x, 30))

