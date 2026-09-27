"""
PauseMenu: the in-game pause overlay. Plain text-and-box buttons, no image
assets needed. Handles its own mouse hover/click and keyboard navigation,
and reports back which action (if any) the player picked — it doesn't
touch game state or audio itself; main.py acts on the returned action.
"""

import pygame

import settings


class PauseMenu:
    # Order matters here — this is the exact order requested: Resume, SFX,
    # Music, Exit to Menu, Exit Game.
    ACTIONS = ["resume", "sfx", "music", "exit_to_menu", "exit_game"]

    def __init__(self):
        font_path = settings.FONTS_DIR / "Fredoka-Bold.ttf"
        self.title_font = pygame.font.Font(str(font_path), 64)
        self.button_font = pygame.font.Font(str(font_path), 32)

        self.selected_index = 0

        button_w, button_h = 420, 64
        spacing = 18
        center_x = settings.SCREEN_WIDTH // 2
        start_y = settings.SCREEN_HEIGHT // 2 - 100

        self.button_rects = {}
        for i, action in enumerate(self.ACTIONS):
            rect = pygame.Rect(0, 0, button_w, button_h)
            rect.center = (center_x, start_y + i * (button_h + spacing))
            self.button_rects[action] = rect

    def _label_for(self, action, audio):
        if action == "resume":
            return "Resume"
        if action == "sfx":
            return f"SFX: {'ON' if audio.sfx_enabled else 'OFF'}"
        if action == "music":
            return f"Music: {'ON' if audio.music_enabled else 'OFF'}"
        if action == "exit_to_menu":
            return "Exit to Menu"
        if action == "exit_game":
            return "Exit Game"
        return action

    def handle_event(self, event, audio):
        """
        Returns one of PauseMenu.ACTIONS if the player chose it this event,
        else None. Doesn't handle Escape — main.py owns pause/resume
        directly so a single Esc press can't open and instantly close this
        menu in the same frame.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.ACTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.ACTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.ACTIONS[self.selected_index]

        elif event.type == pygame.MOUSEMOTION:
            for i, action in enumerate(self.ACTIONS):
                if self.button_rects[action].collidepoint(event.pos):
                    self.selected_index = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, action in enumerate(self.ACTIONS):
                if self.button_rects[action].collidepoint(event.pos):
                    self.selected_index = i
                    return action

        return None

    def draw(self, surface, audio):
        overlay = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        center_x = settings.SCREEN_WIDTH // 2
        title_surf = self.title_font.render("Paused", True, settings.GOLD)
        title_rect = title_surf.get_rect(
            center=(center_x, settings.SCREEN_HEIGHT // 2 - 200)
        )
        surface.blit(title_surf, title_rect)

        for i, action in enumerate(self.ACTIONS):
            rect = self.button_rects[action]
            is_selected = i == self.selected_index
            accent = settings.GOLD if is_selected else settings.WHITE

            if is_selected:
                fill = pygame.Surface(rect.size, pygame.SRCALPHA)
                fill.fill((*accent, 45))
                surface.blit(fill, rect.topleft)

            pygame.draw.rect(surface, accent, rect, width=3, border_radius=10)

            label = self._label_for(action, audio)
            text_surf = self.button_font.render(label, True, accent)
            surface.blit(text_surf, text_surf.get_rect(center=rect.center))
