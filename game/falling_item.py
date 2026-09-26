"""
FallingItem: one object dropping down the screen — poop, a cleaning-liquid
bottle, or a ring, depending on `item_type`. Behavior and appearance for
each type come from settings.ITEM_TYPES, so adding a new item type later
is a data change there, not a new class here.
"""

import random

import settings
from game.asset_utils import load_scaled_sprite


class FallingItem:
    def __init__(self, item_type, lane_x, speed_multiplier=1.0):
        config = settings.ITEM_TYPES[item_type]

        self.item_type = item_type
        self.is_bad = config["is_bad"]
        self.score_value = config["score"]

        self.image = load_scaled_sprite(
            settings.IMAGES_DIR / config["image"],
            config["size"],
        )
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_x
        self.rect.bottom = 0  # start just above the visible screen

        # Float y for smooth, frame-rate-independent falling (same pattern
        # as the toilet's x movement).
        self.y = float(self.rect.y)
        base_speed = random.uniform(*config["speed_range"])
        self.speed = base_speed * speed_multiplier  # pixels per second

    def update(self, dt):
        self.y += self.speed * dt
        self.rect.y = round(self.y)

    def is_off_screen(self):
        return self.rect.top > settings.SCREEN_HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)
