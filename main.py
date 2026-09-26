"""
Entry point. Window setup, game loop, FPS clock, toilet movement, spawner,
collision/scoring, difficulty scaling, and a START / PLAYING / GAME_OVER
state machine.
"""

import sys

import pygame

import settings
from game.player import Toilet
from game.spawner import Spawner
from game.scoreboard import Scoreboard
from game.collisions import resolve_collisions
from game.ui import HUD
from game.audio import AudioManager
from game.pause_menu import PauseMenu


def load_background():
    background = pygame.image.load(str(settings.IMAGES_DIR / "background.png")).convert()
    if background.get_size() != (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT):
        background = pygame.transform.smoothscale(
            background, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
    return background


def new_run():
    """A fresh Toilet + Spawner + Scoreboard — used both at startup and on restart."""
    return Toilet(), Spawner(), Scoreboard()


def main():
    pygame.init()
    pygame.display.set_caption(settings.GAME_TITLE)

    if settings.DEV_MODE:
        flags = 0  # bordered window, same resolution — easier to debug
    else:
        flags = pygame.FULLSCREEN | pygame.SCALED

    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags
    )
    clock = pygame.time.Clock()

    background = load_background()
    hud = HUD()
    audio = AudioManager()
    pause_menu = PauseMenu()

    font_path = settings.FONTS_DIR / "Fredoka-Bold.ttf"
    title_font = pygame.font.Font(str(font_path), 110)
    game_over_font = pygame.font.Font(str(font_path), 96)
    prompt_font = pygame.font.Font(str(font_path), 36)
    instructions_font = pygame.font.Font(str(font_path), 28)

    toilet, spawner, scoreboard = new_run()
    state = "START"  # "START" -> "PLAYING" <-> "PAUSED", "PLAYING" -> "GAME_OVER" -> "PLAYING"
    just_set_high_score = False

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000  # seconds elapsed since last frame
        audio.update(dt)  # advances the delayed game-over -> menu-music sequence, if any

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Esc pauses/resumes during play, and quits from the start
                # or game-over screens. Handled as its own branch (rather
                # than falling through to the PAUSED routing below) so one
                # Esc press can't both open and instantly close the pause
                # menu in the same frame.
                if state == "PLAYING":
                    state = "PAUSED"
                    audio.play_sfx("button_click")
                elif state == "PAUSED":
                    state = "PLAYING"
                    audio.play_sfx("button_click")
                else:
                    running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and state == "START":
                state = "PLAYING"
                audio.play_sfx("button_click")

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and state == "GAME_OVER":
                toilet, spawner, scoreboard = new_run()
                state = "PLAYING"
                just_set_high_score = False
                audio.play_sfx("button_click")

            elif state == "PAUSED":
                # Any other event (keyboard nav, mouse hover/click) while
                # paused goes to the menu itself.
                action = pause_menu.handle_event(event, audio)
                if action == "resume":
                    state = "PLAYING"
                    audio.play_sfx("button_click")
                elif action == "sfx":
                    audio.toggle_sfx()
                    audio.play_sfx("button_click")  # silently no-ops if SFX just got turned off
                elif action == "music":
                    audio.toggle_music()
                    audio.play_sfx("button_click")
                elif action == "exit_to_menu":
                    scoreboard.save_high_score_if_needed()
                    toilet, spawner, scoreboard = new_run()
                    state = "START"
                    audio.play_sfx("button_click")
                elif action == "exit_game":
                    running = False

        if state == "PLAYING":
            keys = pygame.key.get_pressed()
            toilet.handle_input(keys, dt)
            spawner.update(dt, scoreboard.score)
            caught = resolve_collisions(toilet, spawner, scoreboard)
            for item in caught:
                audio.play_sfx("catch_bad" if item.is_bad else "catch_good")

            if scoreboard.is_game_over:
                just_set_high_score = scoreboard.save_high_score_if_needed()
                state = "GAME_OVER"
                audio.trigger_game_over_sequence()

        # Background music follows the current state; play_music() no-ops if
        # that's already what's playing, so calling this every frame is
        # cheap and keeps things in sync after any state change. GAME_OVER
        # is deliberately absent here — its music (silence, then the sting,
        # then menu music) is driven entirely by trigger_game_over_sequence()
        # and audio.update() above, not by per-frame state checks.
        if state == "START":
            audio.play_music("menu")
        elif state == "PLAYING":
            audio.play_music("gameplay")
        # PAUSED deliberately falls through untouched: whatever was already
        # playing (gameplay music) just keeps looping in the background.

        # Draw the scene every frame regardless of state, so items/toilet
        # stay visible (frozen, or simply idle pre-game) behind the
        # start / game-over overlays.
        screen.blit(background, (0, 0))
        spawner.draw(screen)
        toilet.draw(screen)

        if state != "START":
            hud.draw(screen, scoreboard)

        if state == "PAUSED":
            pause_menu.draw(screen, audio)

        if state == "START":
            overlay = pygame.Surface(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            center_x = settings.SCREEN_WIDTH // 2
            center_y = settings.SCREEN_HEIGHT // 2

            title_surf = title_font.render(settings.GAME_TITLE, True, settings.GOLD)
            screen.blit(title_surf, title_surf.get_rect(center=(center_x, center_y - 140)))

            instructions = [
                "Arrow keys or A / D to move the toilet",
                "Catch poop and cleaning liquid for points — avoid the ring!",
            ]
            for i, line in enumerate(instructions):
                line_surf = instructions_font.render(line, True, settings.BROWN)
                screen.blit(
                    line_surf, line_surf.get_rect(center=(center_x, center_y - 30 + i * 36))
                )

            if scoreboard.high_score > 0:
                hs_surf = instructions_font.render(
                    f"High Score: {scoreboard.high_score}", True, settings.GOLD
                )
                screen.blit(hs_surf, hs_surf.get_rect(center=(center_x, center_y + 50)))

            prompt_surf = prompt_font.render("Press SPACE to Play", True, settings.GREEN)
            screen.blit(prompt_surf, prompt_surf.get_rect(center=(center_x, center_y + 110)))

        if state == "GAME_OVER":
            overlay = pygame.Surface(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            center_x = settings.SCREEN_WIDTH // 2
            center_y = settings.SCREEN_HEIGHT // 2

            title_surf = game_over_font.render("GAME OVER!", True, settings.RED)
            screen.blit(title_surf, title_surf.get_rect(center=(center_x, center_y - 60)))

            score_line = f"Score: {scoreboard.score}    High Score: {scoreboard.high_score}"
            if just_set_high_score:
                score_line += "  (New High Score!)"
            score_surf = prompt_font.render(score_line, True, settings.WHITE)
            screen.blit(score_surf, score_surf.get_rect(center=(center_x, center_y + 20)))

            prompt_surf = prompt_font.render(
                "Press R to restart  ·  Esc to quit", True, settings.GOLD
            )
            screen.blit(prompt_surf, prompt_surf.get_rect(center=(center_x, center_y + 70)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
