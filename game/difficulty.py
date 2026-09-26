"""
Difficulty scaling: as the score climbs, items fall faster and spawn more
often, up to a capped maximum so the game ramps up without ever becoming
literally unplayable.
"""

import settings


def get_difficulty_level(score):
    level = score // settings.DIFFICULTY_SCORE_STEP
    return min(level, settings.DIFFICULTY_MAX_LEVEL)


def get_speed_multiplier(score):
    level = get_difficulty_level(score)
    return 1 + level * settings.SPEED_INCREASE_PER_LEVEL


def get_spawn_interval_multiplier(score):
    level = get_difficulty_level(score)
    scale = 1 - level * settings.SPAWN_INTERVAL_DECREASE_PER_LEVEL
    return max(scale, settings.MIN_SPAWN_INTERVAL_SCALE)
