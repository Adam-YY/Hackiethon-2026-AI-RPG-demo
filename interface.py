import pygame
import sys

import game_master

# --- Configuration & Initialization ---
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Post-Magic: Orizon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
GOLD = (212, 175, 55)
BOX_ALPHA = 180

# Fonts
font_stats = pygame.font.SysFont("arial", 24, bold=True)
font_story = pygame.font.SysFont("georgia", 22)
font_button = pygame.font.SysFont("arial", 16)

# --- Load Assets ---
try:
    background = pygame.image.load("city3.jpg")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # BGM Setup
    pygame.mixer.music.load("bgm1.mp3")
    pygame.mixer.music.play(-1)  # Loop indefinitely

except pygame.error:
    print("Warning: background image not found. Using solid color.")
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((30, 30, 30))

def draw_text_centered(text, font, color, rect):
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < rect.width - 40: # Margin inside box
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    total_height = len(lines) * font.get_linesize()
    y_offset = rect.y + (rect.height - total_height) // 2
    
    for line in lines:
        text_surf = font.render(line.strip(), True, color)
        text_rect = text_surf.get_rect(center=(rect.centerx, y_offset + font.get_linesize() // 2))
        screen.blit(text_surf, text_rect)
        y_offset += font.get_linesize()

def run_game():
    clock = pygame.time.Clock()
    state = game_master.initial_state()

    while True:
        mouse_pos = pygame.mouse.get_pos()
        current_text = state["story_text"]
        options = state.get("options") or []
        player_stats = state.get("stats") or {}
        game_over = state.get("game_over", False)

        # Build story display: if game over, append ending title and description
        if game_over and state.get("ending_title"):
            current_text = current_text + "\n\n— " + state["ending_title"] + " —"
            if state.get("ending_description"):
                current_text = current_text + "\n\n" + state["ending_description"]

        # --- UI Layout Logic ---
        story_width, story_height = 850, 350
        story_rect = pygame.Rect((SCREEN_WIDTH - story_width) // 2, 200, story_width, story_height)

        btn_width = 250
        btn_height = 60
        btn_y = 650
        total_buttons_width = len(options) * btn_width + (len(options) - 1) * 50 if options else 0
        start_x = (SCREEN_WIDTH - total_buttons_width) // 2 if options else 0

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                for i in range(len(options)):
                    button_rect = pygame.Rect(start_x + (i * (btn_width + 50)), btn_y, btn_width, btn_height)
                    if button_rect.collidepoint(mouse_pos):
                        state = game_master.advance(state, i)
                        break

        # 2. Rendering
        screen.blit(background, (0, 0))

        # --- Top Stats Bar ---
        stats_bar = pygame.Surface((SCREEN_WIDTH, 50))
        stats_bar.set_alpha(220)
        stats_bar.fill(BLACK)
        screen.blit(stats_bar, (0, 0))

        stat_string = (
            f"HP: {player_stats.get('HP', 0)}   |   Mana: {player_stats.get('Mana', 0)}   |   "
            f"Gold: {player_stats.get('Gold', 0)}   |   Bullets: {player_stats.get('Bullets', 0)}"
        )
        stats_surf = font_stats.render(stat_string, True, GOLD)
        screen.blit(stats_surf, (30, 10))

        # --- Center Story Box ---
        story_surface = pygame.Surface((story_rect.width, story_rect.height))
        story_surface.set_alpha(BOX_ALPHA)
        story_surface.fill(BLACK)
        screen.blit(story_surface, (story_rect.x, story_rect.y))
        pygame.draw.rect(screen, GOLD, story_rect, 3)

        draw_text_centered(current_text, font_story, WHITE, story_rect)

        # --- Bottom Buttons ---
        for i, option in enumerate(options):
            button_rect = pygame.Rect(start_x + (i * (btn_width + 50)), btn_y, btn_width, btn_height)

            is_hovered = button_rect.collidepoint(mouse_pos)
            color = (80, 80, 80) if is_hovered else BLACK
            border_color = WHITE if is_hovered else GOLD

            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)

            btn_text = font_button.render(option, True, WHITE)
            btn_rect = btn_text.get_rect(center=button_rect.center)
            screen.blit(btn_text, btn_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run_game()