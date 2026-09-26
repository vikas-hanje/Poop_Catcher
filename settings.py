"""
Central place for every constant the game uses.
Nothing in here should import from the rest of the `game` package —
this file should be safe to import from anywhere without circular imports.
"""

from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts" / "Fredoka"
DATA_DIR = BASE_DIR / "data"
HIGHSCORE_FILE = DATA_DIR / "highscore.json"

# --- Display ---
GAME_TITLE = "Poop Catcher"
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Set to True while developing: launches a bordered window instead of true
# fullscreen, which makes alt-tabbing / reading tracebacks much easier.
# Flip to False for the "real" build.
DEV_MODE = True

# --- Colors (fallback / debug use only, sprites carry the real look) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 40, 40)
GREEN = (40, 200, 90)
GOLD = (230, 190, 60)
BROWN = (217, 165, 22)

# --- Player (Toilet) ---
TOILET_WIDTH = 170
TOILET_HEIGHT = 280
TOILET_SPEED = 900            # pixels per second
TOILET_BOTTOM_MARGIN = 40     # gap between toilet sprite and bottom edge

# --- Falling items (width, height) ---
POOP_SIZE = (55, 55)
BOTTLE_SIZE = (40, 99)
RING_SIZE = (40, 40)
PLUNGER_SIZE = (50, 65)       # reserved for future power-up
LIFE_ICON_SIZE = (40, 40)

# --- Lanes ---
# 5 evenly spaced spawn columns across the screen width, with margins on
# either side so items don't spawn flush against the screen edges.
NUM_LANES = 5
LANE_MARGIN = SCREEN_WIDTH // (NUM_LANES + 1)
LANE_X_POSITIONS = [LANE_MARGIN * (i + 1) for i in range(NUM_LANES)]

# --- Gameplay ---
STARTING_LIVES = 4
GOOD_ITEM_SCORE = 10
BONUS_ITEM_SCORE = 25

# --- Falling item types ---
# One shared table drives everything about each item: which image and size
# to use, how fast it falls, what it's worth, and how often it shows up
# relative to the others. "weight" is just a relative likelihood — it
# doesn't need to add up to 100, random.choices() normalizes it for us.
ITEM_TYPES = {
    "poop": {
        "image": "poop.png",
        "size": POOP_SIZE,
        "speed_range": (300, 500),    # pixels per second, randomized per item
        "score": GOOD_ITEM_SCORE,
        "is_bad": False,
        "weight": 65,
    },
    "bottle": {
        "image": "cleaning_liquid_bottle.png",
        "size": BOTTLE_SIZE,
        "speed_range": (300, 500),
        "score": BONUS_ITEM_SCORE,
        "is_bad": False,
        "weight": 15,
    },
    "ring": {
        "image": "ring.png",
        "size": RING_SIZE,
        "speed_range": (350, 550),    # a little faster — reads as "danger"
        "score": 0,
        "is_bad": True,
        "weight": 20,
    },
}

# Each lane waits a random amount of time in this range before dropping its
# next item, so lanes don't all fire in lockstep.
SPAWN_INTERVAL_RANGE = (0.6, 1.6)     # seconds

# --- Difficulty scaling ---
# Every DIFFICULTY_SCORE_STEP points, the game gets one "level" harder:
# items fall a bit faster and spawn a bit more often. Capped at
# DIFFICULTY_MAX_LEVEL so it ramps up but never becomes literally
# unplayable.
DIFFICULTY_SCORE_STEP = 100            # points needed per difficulty level
DIFFICULTY_MAX_LEVEL = 10              # levels beyond this have no extra effect
SPEED_INCREASE_PER_LEVEL = 0.08        # +8% fall speed per level
SPAWN_INTERVAL_DECREASE_PER_LEVEL = 0.06   # -6% spawn interval per level
MIN_SPAWN_INTERVAL_SCALE = 0.4         # never shrink spawn interval below 40% of base

# --- Audio ---
SFX_VOLUME = 0.7
MUSIC_VOLUME = 0.4
GAME_OVER_SOUND_DELAY = 1.0     # seconds of silence after death, before the game-over sting plays
