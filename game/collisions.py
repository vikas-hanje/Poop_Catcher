"""
Collision checking between the toilet and falling items.
"""


def resolve_collisions(toilet, spawner, scoreboard):
    """
    Check the toilet's rect against every currently-falling item's rect
    with pygame's Rect.colliderect() — the core "does A overlap B" check
    this game is built around.

    On a hit: good items add score, the ring costs a life. Either way the
    item is removed from play (a caught ring shouldn't linger on screen).

    Returns the list of items caught this frame, so the caller can trigger
    per-catch effects (sounds, particles) later without this function
    needing to know about them.
    """
    caught = []
    remaining = []

    for item in spawner.items:
        if toilet.rect.colliderect(item.rect):
            caught.append(item)
            if item.is_bad:
                scoreboard.lose_life()
            else:
                scoreboard.add_score(item.score_value)
        else:
            remaining.append(item)

    spawner.items = remaining
    return caught
