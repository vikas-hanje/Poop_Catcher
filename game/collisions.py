"""
Collision checking between the toilet and falling items.
"""


def resolve_collisions(toilet, spawner, scoreboard):
    """
    Checks the toilet's collision_rect (the bowl only, not the full
    sprite — see Toilet.collision_rect) against every falling item's rect.
    Good catches add score, the ring costs a life; either way the item is
    removed from play. Returns the items caught this frame, so the caller
    can trigger per-catch effects (sounds, etc.) without this function
    needing to know about them.
    """
    caught = []
    remaining = []

    for item in spawner.items:
        if toilet.collision_rect.colliderect(item.rect):
            caught.append(item)
            if item.is_bad:
                scoreboard.lose_life()
            else:
                scoreboard.add_score(item.score_value)
        else:
            remaining.append(item)

    spawner.items = remaining
    return caught
