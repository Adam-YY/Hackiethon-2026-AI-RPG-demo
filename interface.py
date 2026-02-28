import pygame
import pygame_gui
import re
from pygame_gui.elements import UIPanel, UITextBox, UIButton, UITextEntryLine, UILabel
from pygame_gui.core import ObjectID
from typing import List, Optional, Dict
from models import Player, Scene, Option

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
HUD_HEIGHT = 60
DIALOGUE_HEIGHT = 200
LOG_WIDTH = 320  # Approx 25% of 1280
FPS = 60

class VisualNovelUI:
    def __init__(self, theme_path: str = "assets/themes/theme.json"):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Iron Skeleton - Neuro-Symbolic Engine")
        
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path)
        
        # Preload specific fonts to resolve UserWarnings for bold text/HTML tags
        # We only preload the bold version as the regular one is already loaded by the theme
        self.manager.preload_fonts([
            {'name': 'arial', 'point_size': 20, 'style': 'bold', 'antialiased': '1'}
        ])

        self.clock = pygame.time.Clock()
        
        self.background_image: Optional[pygame.Surface] = None
        self.current_bg_path: str = ""
        
        # UI Elements
        self.hud_panel: Optional[UIPanel] = None
        self.stat_labels: Dict[str, UILabel] = {}
        self.log_box: Optional[UITextBox] = None
        self.dialogue_box: Optional[UITextBox] = None
        self.option_buttons: List[UIButton] = []
        self.custom_action_input: Optional[UITextEntryLine] = None
        
        self.floating_notes: List[UITextBox] = []
        self.story_history: str = "<b>STORY LOG</b>"
        
        # Narrative State
        self.full_narrative: str = ""
        self.text_chunks: List[str] = []
        self.current_chunk_idx: int = 0
        self.is_typing: bool = False
        
        self.selected_choice: Optional[str] = None
        
        self._setup_layout()

    def _setup_layout(self):
        # 1. HUD Bar (Top)
        self.hud_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, WIDTH, HUD_HEIGHT),
            manager=self.manager,
            object_id=ObjectID(class_id="@hud_panel")
        )
        
        stats = ["HP", "Mana", "Bullets", "Credits"]
        spacing = WIDTH // len(stats)
        for i, stat in enumerate(stats):
            label = UILabel(
                relative_rect=pygame.Rect(i * spacing, 0, spacing, HUD_HEIGHT),
                text=f"{stat}: 0",
                manager=self.manager,
                container=self.hud_panel
            )
            self.stat_labels[stat.lower()] = label

        # 2. Story Log (Right Side)
        self.log_box = UITextBox(
            html_text="<b>STORY LOG</b><br>",
            relative_rect=pygame.Rect(WIDTH - LOG_WIDTH, HUD_HEIGHT, LOG_WIDTH, HEIGHT - HUD_HEIGHT),
            manager=self.manager,
            object_id=ObjectID(class_id="@log_box")
        )

        # 3. Dialogue Box (Bottom)
        self.dialogue_box = UITextBox(
            html_text="",
            relative_rect=pygame.Rect(20, HEIGHT - DIALOGUE_HEIGHT - 20, WIDTH - LOG_WIDTH - 40, DIALOGUE_HEIGHT),
            manager=self.manager
        )

    def update_hud(self, player: Player):
        self.stat_labels["hp"].set_text(f"HP: {player.hp}")
        self.stat_labels["mana"].set_text(f"Mana: {player.mana}")
        self.stat_labels["bullets"].set_text(f"Bullets: {player.bullet}")
        self.stat_labels["credits"].set_text(f"Credits: {player.credits}")

    def clear_ui(self):
        """Wipes the UI elements clean for a fresh session."""
        # CRITICAL: Kill active effects to prevent text overlap
        self.dialogue_box.set_active_effect(None)
        self.dialogue_box.set_text("")
        
        # Clear Narrative Buffers
        self.full_narrative = ""
        self.text_chunks = []
        self.current_chunk_idx = 0
        self.is_typing = False
        
        # Reset Story Log history
        self.story_history = "<b>STORY LOG</b>"
        self.log_box.set_text(self.story_history)
        
        # Clear options and notes
        self.clear_options()
        for note in self.floating_notes[:]:
            note.kill()
        self.floating_notes.clear()

    def show_message(self, text: str):
        """Splits narrative into chunks of 3 sentences and displays the first."""
        text = text.strip()
        # Only skip if we are already in the middle of showing THIS exact narrative
        if text == self.full_narrative and self.is_typing:
            return
            
        self.full_narrative = text
        self.text_chunks = self._split_sentences(text)
        self.current_chunk_idx = 0
        self._display_current_chunk()

    def _split_sentences(self, text: str) -> List[str]:
        if not text: return ["..."]
        # Use findall to avoid look-behind issue, and capture sentences ending with punctuation.
        sentences = re.findall(r'[^.!?]+[.!?]["”\']?|[^.!?]+$', text.strip())

        # Filter empty strings and ensure at least one chunk exists
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences: return ["..."]
        
        chunks = []
        for i in range(0, len(sentences), 3):
            chunks.append(" ".join(sentences[i:i+3]))
        return chunks

    def _display_current_chunk(self):
        if not self.text_chunks: return
        chunk = self.text_chunks[self.current_chunk_idx]
        
        # 1. Kill any existing effect and completely clear the box
        self.dialogue_box.set_active_effect(None)
        self.dialogue_box.set_text("")
        
        # 2. Force a micro-update to ensure the 'empty' state is registered internally
        self.manager.update(0.01)
        
        # 3. Set the new text and state
        self.is_typing = True
        self.dialogue_box.set_text(chunk)
        
        # 4. Apply the typewriter effect
        # The effect will now start from a truly empty text box
        self.dialogue_box.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR, 
                                          params={'time_per_letter': 0.05})

    def next_chunk(self) -> bool:
        """Advances to the next 3-sentence chunk. Returns False if done."""
        if self.is_typing:
            # Skip typewriter effect for current chunk
            self.dialogue_box.set_active_effect(None)
            self.dialogue_box.set_text(self.text_chunks[self.current_chunk_idx])
            self.is_typing = False
            return True
        
        if self.current_chunk_idx + 1 < len(self.text_chunks):
            self.current_chunk_idx += 1
            self._display_current_chunk()
            return True
        return False

    def append_story_log(self, text: str):
        """Only appends USER INPUT to the log box."""
        self.story_history += f"<br><br><font color='#00ffcc'><b>{text}</b></font>"
        self.log_box.set_text(self.story_history)
        if self.log_box.scroll_bar:
            self.log_box.scroll_bar.set_scroll_from_start_percentage(1.0)

    def draw_background(self, image_path: str):
        if image_path != self.current_bg_path:
            try:
                img = pygame.image.load(image_path).convert()
                self.background_image = pygame.transform.scale(img, (WIDTH, HEIGHT))
                self.current_bg_path = image_path
            except Exception as e:
                print(f"Error loading background {image_path}: {e}")
                self.background_image = None
        
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((40, 40, 40))

    def spawn_floating_notification(self, text: str, color_hex: str = "#00ffcc"):
        """Creates a temporary notification that floats up and fades."""
        import random
        start_x = (WIDTH - LOG_WIDTH) // 2 + random.randint(-100, 100)
        start_y = HEIGHT // 2 + random.randint(-50, 50)
        
        note = UITextBox(
            html_text=f'<font color={color_hex}>{text}</font>',
            relative_rect=pygame.Rect(start_x, start_y, 250, 50),
            manager=self.manager,
            object_id=ObjectID(class_id="@floating_note")
        )
        note.set_active_effect(pygame_gui.TEXT_EFFECT_FADE_OUT)
        self.floating_notes.append(note)

    def _update_floating_notes(self):
        """Moves notes upwards."""
        for note in self.floating_notes[:]:
            rect = note.get_relative_rect()
            note.set_relative_position((rect.x, rect.y - 1))

    def clear_options(self):
        for btn in self.option_buttons:
            btn.kill()
        self.option_buttons.clear()
        if self.custom_action_input:
            self.custom_action_input.kill()
            self.custom_action_input = None

    def display_options(self, options: List[Option]):
        self.clear_options()
        self.selected_choice = None
        
        btn_width = 350
        btn_height = 40
        start_x = 100
        start_y = 150
        
        for i, opt in enumerate(options):
            btn = UIButton(
                relative_rect=pygame.Rect(start_x, start_y + i * 50, btn_width, btn_height),
                text=opt.text,
                manager=self.manager,
                tool_tip_text=f"Select Option {opt.id}"
            )
            btn.user_data = str(opt.id)
            self.option_buttons.append(btn)
        
        custom_btn = UIButton(
            relative_rect=pygame.Rect(start_x, start_y + len(options) * 50, btn_width, btn_height),
            text="[Take Custom Action]",
            manager=self.manager,
            object_id=ObjectID(class_id="@custom_btn")
        )
        custom_btn.user_data = "CUSTOM_TRIGGER"
        self.option_buttons.append(custom_btn)

    def display_end_options(self):
        """Displays Retry and Quit buttons when the game ends."""
        self.clear_options()
        self.selected_choice = None
        
        btn_width = 350
        btn_height = 50
        # Centering the buttons
        start_x = (WIDTH - LOG_WIDTH) // 2 - btn_width // 2
        start_y = HEIGHT // 2 - 50
        
        retry_btn = UIButton(
            relative_rect=pygame.Rect(start_x, start_y, btn_width, btn_height),
            text="RETRY SESSION",
            manager=self.manager,
            object_id=ObjectID(class_id="@retry_btn")
        )
        retry_btn.user_data = "RETRY"
        self.option_buttons.append(retry_btn)
        
        quit_btn = UIButton(
            relative_rect=pygame.Rect(start_x, start_y + 70, btn_width, btn_height),
            text="QUIT TO DESKTOP",
            manager=self.manager,
            object_id=ObjectID(class_id="@quit_btn")
        )
        quit_btn.user_data = "QUIT"
        self.option_buttons.append(quit_btn)

    def _open_custom_input(self):
        for btn in self.option_buttons:
            btn.hide()
        
        self.custom_action_input = UITextEntryLine(
            relative_rect=pygame.Rect(100, 250, 600, 50),
            manager=self.manager
        )
        self.custom_action_input.focus()

    def handle_events(self) -> Optional[str]:
        """Main event loop integration point."""
        time_delta = self.clock.tick(FPS) / 1000.0
        result = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            self.manager.process_events(event)
            
            # Click detection
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Advance if clicking dialogue or empty space
                    # Ignore if clicking UI elements like the log box area
                    is_log_click = self.log_box.get_relative_rect().collidepoint(event.pos)
                    if not is_log_click:
                        result = "CLICKED"
            
            # Typewriter sync & Floating Note cleanup
            if event.type == pygame_gui.UI_TEXT_EFFECT_FINISHED:
                if event.ui_element == self.dialogue_box:
                    self.is_typing = False
                # Use 'try...except' because a note might be removed twice
                # if events are processed in a strange order.
                try:
                    if event.ui_element in self.floating_notes:
                        event.ui_element.kill()
                        self.floating_notes.remove(event.ui_element)
                except ValueError:
                    pass # note already removed, do nothing
            
            # Choice detection
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                user_data = getattr(event.ui_element, 'user_data', None)
                if user_data == "CUSTOM_TRIGGER":
                    self._open_custom_input()
                elif user_data:
                    result = user_data
            
            # Text input detection
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == self.custom_action_input:
                    result = event.text

        self._update_floating_notes()
        self.manager.update(time_delta)
        return result

    def render(self):
        self.manager.draw_ui(self.screen)
        pygame.display.flip()

# Integration Helper
def run_game_loop(gm, ui: VisualNovelUI, bg_path: str):
    """
    Revised Game Loop for GameMaster integration.
    """
    while True:
        # 1. ABSOLUTE RESET: Wipe UI and GM state before starting
        ui.clear_ui()
        gm.reset_game()

        output, _ = gm.run_turn()
        pygame.event.clear()  # BUGFIX: Clear events queued during initial load

        while True:
            # Check for immediate stat-based Game Over
            game_over_msg = gm.check_game_over()
            display_output = output
            if game_over_msg:
                display_output = f"{output} {game_over_msg}"
            
            ui.draw_background(bg_path)
            ui.update_hud(gm.state.player)
            ui.show_message(display_output)

            # Narrative Stream Phase (Wait for user to read/click through chunks)
            streaming_done = False
            while not streaming_done:
                status = ui.handle_events()
                if status == "QUIT":
                    pygame.quit()
                    return

                if status == "CLICKED":
                    if not ui.next_chunk():
                        streaming_done = True

                ui.draw_background(bg_path)
                ui.render()

            # End State Check (HP loss OR narrative 'is_end')
            current_scene = gm.get_current_scene()
            if game_over_msg or current_scene.is_end:
                # Show End Screen Buttons
                ui.display_end_options()
                
                final_choice = None
                while final_choice not in ["RETRY", "QUIT"]:
                    final_choice = ui.handle_events()
                    if final_choice == "QUIT":
                        pygame.quit()
                        return
                    
                    ui.draw_background(bg_path)
                    ui.render()
                
                if final_choice == "RETRY":
                    break # Break inner loop to restart via the outer loop
                else:
                    pygame.quit()
                    return

            # Choice Selection Phase
            ui.display_options(current_scene.options)

            choice = None
            while choice is None:
                choice = ui.handle_events()
                if choice == "QUIT":
                    pygame.quit()
                    return
                elif choice == "CLICKED":
                    choice = None  # Ignore clicks that aren't button presses here

                ui.draw_background(bg_path)
                ui.render()

            # Record Choice
            choice_text = ""
            if choice.isdigit():
                opt = next((o for o in current_scene.options if str(o.id) == choice), None)
                choice_text = f"> {opt.text}" if opt else f"> {choice}"
            else:
                choice_text = f"> {choice}"

            ui.append_story_log(choice_text)

            # Process turn
            output, _ = gm.run_turn(choice)
            pygame.event.clear()
            ui.clear_options()

def main():
    from game_master import GameMaster
    ui = VisualNovelUI()
    gm = GameMaster("WasteLand", on_stat_change=ui.spawn_floating_notification)
    run_game_loop(gm, ui, "assets/themes/WasteLand/city3.jpg")

if __name__ == "__main__":
    main()
