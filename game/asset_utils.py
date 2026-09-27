"""
Shared helpers for loading image assets consistently across the game.
"""

import pygame


def load_scaled_sprite(path, target_size):
    """
    Load an image, trim any transparent padding around the artwork, then
    scale it to exactly `target_size`. Several of our exported PNGs have
    empty padding baked into their canvas — scaling the raw canvas would
    scale that padding too, making the visible art smaller than intended.
    """
    raw = pygame.image.load(str(path)).convert_alpha()

    content_rect = raw.get_bounding_rect()
    trimmed = raw.subsurface(content_rect).copy()

    return pygame.transform.smoothscale(trimmed, target_size)
