"""
Spawner: owns the list of currently-falling items and decides when new
ones appear.

Each of the settings.NUM_LANES lanes runs its own independent timer, so
several items can be falling in different columns at once without ever
spawning on top of each other in the same lane.
"""

import random

import settings
from game.falling_item import FallingItem
from game.difficulty import get_speed_multiplier, get_spawn_interval_multiplier


class Spawner:
    def __init__(self):
        self.items = []
        self.lane_timers = [
            self._random_interval() for _ in settings.LANE_X_POSITIONS
        ]

    def _random_interval(self):
        return random.uniform(*settings.SPAWN_INTERVAL_RANGE)

    def _random_item_type(self):
        types = list(settings.ITEM_TYPES.keys())
        weights = [settings.ITEM_TYPES[t]["weight"] for t in types]
        return random.choices(types, weights=weights, k=1)[0]

    def update(self, dt, score=0):
        speed_multiplier = get_speed_multiplier(score)
        interval_multiplier = get_spawn_interval_multiplier(score)

        # Count down each lane's timer; spawn and reset when it runs out.
        for lane_index, lane_x in enumerate(settings.LANE_X_POSITIONS):
            self.lane_timers[lane_index] -= dt
            if self.lane_timers[lane_index] <= 0:
                item_type = self._random_item_type()
                self.items.append(
                    FallingItem(item_type, lane_x, speed_multiplier=speed_multiplier)
                )
                self.lane_timers[lane_index] = self._random_interval() * interval_multiplier

        for item in self.items:
            item.update(dt)

        # Drop anything that's fallen past the bottom of the screen.
        self.items = [item for item in self.items if not item.is_off_screen()]

    def draw(self, surface):
        for item in self.items:
            item.draw(surface)
