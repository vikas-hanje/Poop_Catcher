"""
The Toilet class: the player-controlled catcher at the bottom of the screen.
"""

import pygame

import settings
from game.asset_utils import load_scaled_sprite


class Toilet:
    def __init__(self):
        self.image = load_scaled_sprite(
            settings.IMAGES_DIR / "toilet.png",
            (settings.TOILET_WIDTH, settings.TOILET_HEIGHT),
        )

        self.rect = self.image.get_rect()
        self.rect.centerx = settings.SCREEN_WIDTH // 2
        self.rect.bottom = settings.SCREEN_HEIGHT - settings.TOILET_BOTTOM_MARGIN

        # Track position as a float separately from the rect (which only
        # accepts ints) so movement stays smooth at any frame rate instead
        # of snapping to whole-pixel steps.
        self.x = float(self.rect.x)
        self.speed = settings.TOILET_SPEED  # pixels per second

    def handle_input(self, keys, dt):
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        self.x += direction * self.speed * dt

        # Clamp so the toilet can't move past the screen edges.
        max_x = settings.SCREEN_WIDTH - self.rect.width
        self.x = max(0, min(self.x, max_x))
        self.rect.x = round(self.x)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
