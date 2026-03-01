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
DIALOGUE_HEIGHT = 350  # Expanded for professional VN feel (~48% of 720px)
LOG_WIDTH = 320        # Approx 25% of 1280
FPS = 60

class VisualNovelUI:
    def __init__(self, theme_path: str = "assets/themes/theme.json"):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Iron Skeleton - Neuro-Symbolic Engine")
        
        # UI Manager Loading the custom theme
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path)
        
        # Preload specific fonts to resolve UserWarnings for bold/italic HTML tags
        # arial_bold_aa_22 is already loaded via theme.json for text_box, so only preload others needed
        self.manager.preload_fonts([
            {'name': 'arial', 'point_size': 22, 'style': 'italic', 'antialiased': '1'},
            {'name': 'arial', 'point_size': 18, 'style': 'bold', 'antialiased': '1'}
        ])

        self.clock = pygame.time.Clock()
        
        self.background_image: Optional[pygame.Surface] = None
        self.current_bg_path: str = ""
        
        # UI Elements
        self.hud_panel: Optional[UIPanel] = None
        self.stat_labels: Dict[str, UILabel] = {}
        self.log_box: Optional[UITextBox] = None
        self.dialogue_box: Optional[UITextBox] = None
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
        """Initializes the spatial hierarchy of the UI."""
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

        # 2. Story Log (Right Sidebar)
        self.log_box = UITextBox(
            html_text="<b>STORY LOG</b><br>",
            relative_rect=pygame.Rect(WIDTH - LOG_WIDTH, HUD_HEIGHT, LOG_WIDTH, HEIGHT - HUD_HEIGHT),
            manager=self.manager,
            object_id=ObjectID(class_id="@log_box")
        )

        # 3. Expanded Dialogue Box (Bottom Anchor)
        # Positioned with a 20px padding from the bottom and sides
        self.dialogue_box = UITextBox(
            html_text="",
            relative_rect=pygame.Rect(
                20, 
                HEIGHT - DIALOGUE_HEIGHT - 20, 
                WIDTH - LOG_WIDTH - 40, 
                DIALOGUE_HEIGHT
            ),
            manager=self.manager
        )

    def update_hud(self, player: Player):
        self.stat_labels["hp"].set_text(f"HP: {player.hp}")
        self.stat_labels["mana"].set_text(f"Mana: {player.mana}")
        self.stat_labels["bullets"].set_text(f"Bullets: {player.bullet}")
        self.stat_labels["credits"].set_text(f"Credits: {player.credits}")

    def play_bgm(self, music_path: str, loops: int = -1):
        """Starts background music playback."""
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"Error playing music {music_path}: {e}")

    def stop_bgm(self):
        """Stops background music playback."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def clear_ui(self):
        """Wipes the UI elements clean for a fresh session."""
        self.dialogue_box.set_active_effect(None)
        self.dialogue_box.set_text("")
        
        self.full_narrative = ""
        self.text_chunks = []
        self.current_chunk_idx = 0
        self.is_typing = False
        
        self.story_history = "<b>STORY LOG</b>"
        self.log_box.set_text(self.story_history)
        
        self.clear_options()
        for note in self.floating_notes[:]:
            note.kill()
        self.floating_notes.clear()

    def show_message(self, text: str):
        """Splits narrative into chunks and displays the first. Also logs to Story Log."""
        # BUGFIX: Aggressive ASCII Normalization
        # Standardize whitespace and convert smart quotes/symbols to ASCII.
        # This ensures the typewriter mask matches the rendered text length perfectly.
        text = " ".join(text.split())
        text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        text = text.replace('—', '--').replace('…', '...')
        text = text.encode("ascii", "ignore").decode("ascii")
        
        # HIDDEN COMMANDS: Strip [AI TAKEOVER: ...] tags
        text = re.sub(r'\[AI TAKEOVER:.*?\]', '', text)
        
        if text == self.full_narrative:
            return
            
        self.full_narrative = text
        self.text_chunks = self._split_sentences(text)
        self.current_chunk_idx = 0

        # BUGFIX: Add the narrative text to the Story Log ONLY ONCE
        clean_log_text = re.sub(r'<[^>]+>', '', text) 
        self.story_history += f"<br><br>{clean_log_text}"
        self.log_box.set_text(self.story_history)
        if self.log_box.scroll_bar:
            self.log_box.scroll_bar.set_scroll_from_start_percentage(1.0)

        self._display_current_chunk()

    def _split_sentences(self, text: str) -> List[str]:
        if not text: return ["..."]
        sentences = re.findall(r'[^.!?]+[.!?]["”\']?|[^.!?]+$', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences: return ["..."]
        
        chunks = []
        for i in range(0, len(sentences), 3):
            chunks.append(" ".join(sentences[i:i+3]))
        return chunks

    def _display_current_chunk(self):
        if not self.text_chunks: return
        chunk = self.text_chunks[self.current_chunk_idx]
        
        # 1. Hard Reset and Visual Lock
        self.dialogue_box.set_active_effect(None)
        self.dialogue_box.set_text("")
        self.dialogue_box.hide()
        
        # 2. Pre-Sync: Clear old layout data
        self.manager.update(0.01)
        
        # 3. Layout Initialization: Set text while hidden
        self.is_typing = True
        self.dialogue_box.set_text(chunk)
        
        # 4. MASK SYNCHRONIZATION
        # Update multiple times to ensure internal HTML parsing is complete
        for _ in range(3):
            self.manager.update(0.01)
        
        # 5. Apply Effect to stabilized layout
        self.dialogue_box.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR, 
                                          params={'time_per_letter': 0.05})
        
        # 6. Final Tick & Reveal
        self.manager.update(0.01)
        self.dialogue_box.show()
        
        # Ensure we start at the top of long chunks
        if self.dialogue_box.scroll_bar:
            self.dialogue_box.scroll_bar.set_scroll_from_start_percentage(0.0)
        
        # 4. Apply Effect: Initialize the typewriter mask
        self.dialogue_box.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR, 
                                          params={'time_per_letter': 0.05})
        
        # 5. TRIPLE-SYNC: Force the engine to process the mask BEFORE revealing
        # This prevents the 'ghost frame' where the end of the text shows
        self.manager.update(0.01)
        self.manager.update(0.01)
        self.manager.update(0.01)
        
        self.dialogue_box.show()
        
        # Ensure we start at the top of long chunks
        if self.dialogue_box.scroll_bar:
            self.dialogue_box.scroll_bar.set_scroll_from_start_percentage(0.0)

    def next_chunk(self) -> bool:
        """Advances to the next text chunk. Returns False if done."""
        if self.is_typing:
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

    def spawn_floating_notification(self, text: str, color_hex: any = "#00ffcc"):
        import random
        # Convert RGB tuple to Hex string if necessary for HTML color tag
        if isinstance(color_hex, tuple):
            color_hex = '#%02x%02x%02x' % color_hex

        start_x = (WIDTH - LOG_WIDTH) // 2 + random.randint(-150, 150)
        start_y = HEIGHT // 2 + random.randint(-100, 50)
        
        note = UITextBox(
            html_text=f'<b><font color={color_hex} size=5>{text}</font></b>',
            relative_rect=pygame.Rect(start_x, start_y, 300, 60),
            manager=self.manager,
            object_id=ObjectID(class_id="@floating_note")
        )
        note.set_active_effect(pygame_gui.TEXT_EFFECT_FADE_OUT)
        self.floating_notes.append(note)

    def _update_floating_notes(self):
        for note in self.floating_notes[:]:
            rect = note.get_relative_rect()
            note.set_relative_position((rect.x, rect.y - 1))

    def clear_options(self):
        if self.custom_action_input:
            self.custom_action_input.kill()
            self.custom_action_input = None

    def display_options(self, options: List[Option]):
        """Injects polished HTML hyperlinks into the dialogue flow."""
        self.selected_choice = None
        # Use the raw text of the current chunk to avoid duplicating appended links
        current_text = self.text_chunks[self.current_chunk_idx]
        
        links_html = ""
        for opt in options:
            # Clean line breaks for standard options
            links_html += f'<br><br><a href="{opt.id}">> {opt.text}</a>'
        
        # Stylized Custom Action link with soft teal color and italics
        links_html += (
            '<br><br>'
            '<a href="CUSTOM_TRIGGER">'
            '<font color="#80acaa"><i>> Take Custom Action (Free type)</i></font>'
            '</a>'
        )
        
        self.dialogue_box.set_text(current_text + links_html)
        
        if self.dialogue_box.scroll_bar:
            self.dialogue_box.scroll_bar.set_scroll_from_start_percentage(1.0)

    def display_end_options(self):
        """Displays Retry and Quit as prominent links."""
        self.selected_choice = None
        current_text = self.dialogue_box.html_text
        
        end_links = (
            '<br><br><br>'
            '<font color="#ff0055">'
            '<a href="RETRY">RETRY SESSION</a>'
            '</font>'
            '<br><br>'
            '<a href="QUIT">QUIT TO DESKTOP</a>'
        )
        
        self.dialogue_box.set_text(current_text + end_links)
        if self.dialogue_box.scroll_bar:
            self.dialogue_box.scroll_bar.set_scroll_from_start_percentage(1.0)

    def _open_custom_input(self):
        """Spawns the text entry line centered above the dialogue box."""
        self.custom_action_input = UITextEntryLine(
            relative_rect=pygame.Rect(100, HEIGHT - DIALOGUE_HEIGHT - 90, 600, 50),
            manager=self.manager
        )
        self.custom_action_input.focus()

    def handle_events(self) -> Optional[str]:
        time_delta = self.clock.tick(FPS) / 1000.0
        result = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            self.manager.process_events(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_log_click = self.log_box.get_relative_rect().collidepoint(event.pos)
                    if not is_log_click:
                        result = "CLICKED"
            
            if event.type == pygame_gui.UI_TEXT_EFFECT_FINISHED:
                if event.ui_element == self.dialogue_box:
                    self.is_typing = False
                try:
                    if event.ui_element in self.floating_notes:
                        event.ui_element.kill()
                        self.floating_notes.remove(event.ui_element)
                except ValueError:
                    pass
            
            # Hyperlink interaction logic
            if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                link = event.link_target
                if link == "CUSTOM_TRIGGER":
                    self._open_custom_input()
                elif link in ["RETRY", "QUIT"]:
                    result = link
                else:
                    result = link
            
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == self.custom_action_input:
                    result = event.text

        self._update_floating_notes()
        self.manager.update(time_delta)
        return result

    def render(self):
        self.manager.draw_ui(self.screen)
        pygame.display.flip()

# --- Shared Game Loop ---
def run_game_loop(gm, ui: VisualNovelUI, bg_path: str):
    while True:
        ui.clear_ui()
        gm.reset_game()

        output, _ = gm.run_turn()
        pygame.event.clear()

        while True:
            game_over_msg = gm.check_game_over()
            display_output = output
            if game_over_msg:
                display_output = f"{output} {game_over_msg}"
            
            ui.draw_background(bg_path)
            ui.update_hud(gm.state.player)
            ui.show_message(display_output)

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

            current_scene = gm.get_current_scene()
            if game_over_msg or current_scene.is_end:
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
                    break
                else:
                    pygame.quit()
                    return

            ui.display_options(current_scene.options)

            choice = None
            while choice is None:
                choice = ui.handle_events()
                if choice == "QUIT":
                    pygame.quit()
                    return
                elif choice == "CLICKED":
                    choice = None

                ui.draw_background(bg_path)
                ui.render()

            choice_text = ""
            if choice.isdigit():
                opt = next((o for o in current_scene.options if str(o.id) == choice), None)
                choice_text = f"> {opt.text}" if opt else f"> {choice}"
            else:
                choice_text = f"> {choice}"

            ui.append_story_log(choice_text)

            output, _ = gm.run_turn(choice)
            pygame.event.clear()
            ui.clear_options()

def main():
    from game_master import GameMaster
    ui = VisualNovelUI()
    gm = GameMaster("WasteLand", on_stat_change=ui.spawn_floating_notification)
    ui.play_bgm("assets/themes/WasteLand/bgm1.mp3")
    run_game_loop(gm, ui, "assets/themes/WasteLand/city3.jpg")

if __name__ == "__main__":
    main()
