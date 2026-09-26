"""
Shared helpers for loading image assets consistently across the game.
"""

import pygame


def load_scaled_sprite(path, target_size):
    """
    Load an image, trim any transparent padding around the artwork, then
    scale the trimmed artwork to exactly `target_size` (width, height).

    Several of our exported PNGs (icon-pack exports) have empty transparent
    space around the actual drawing, inside their canvas. Scaling the raw
    canvas straight to a target size scales that padding too, so the visible
    art ends up smaller than intended. Trimming to the actual drawn content
    first means every sprite reliably fills the size you ask for, and later
    collision rects line up with what the player actually sees.
    """
    raw = pygame.image.load(str(path)).convert_alpha()

    content_rect = raw.get_bounding_rect()
    trimmed = raw.subsurface(content_rect).copy()

    return pygame.transform.smoothscale(trimmed, target_size)
