import time
from typing import List, Optional
from models import WorldState, Scene, Option, GameContext
from loader import ThemeLoader
from systems import NarrativeLogger, MemoryManager, EventManager
from AI_model import call_ai_game_master
import world

class GameMaster:
    """
    The Director: A Dual-Mode State Machine for the Post-Magic RPG.
    Phase 2: Neuro-Symbolic Integration.
    """

    def __init__(self, theme_name: str, on_stat_change=None):
        theme_path = f"assets/themes/{theme_name}"
        loader = ThemeLoader(theme_path)
        
        self.story = loader.load_story()
        self.state = world.load_world_from_theme(loader)
        
        # Systems
        self.logger = NarrativeLogger()
        self.memory = MemoryManager()
        self.events = EventManager()
        self.events.load_triggers(loader.load_events())

        # Context
        self.context = GameContext()

        # Callbacks
        self.on_stat_change = on_stat_change

        # AI Control
        self.mode_b_active = False # Mode B: AI Takeover
        self.custom_ai_rounds = 0

    def reset_game(self, theme_name: str = "WasteLand"):
        """Resets the game state, memory, and logs for a new player."""
        theme_path = f"assets/themes/{theme_name}"
        loader = ThemeLoader(theme_path)
        
        self.state = world.load_world_from_theme(loader)
        self.memory.reset_game()
        self.logger.reset_game()
        self.context = GameContext()
        self.mode_b_active = False
        self.custom_ai_rounds = 0

    def get_current_scene(self) -> Scene:
        return self.state.scenes[self.state.player.current_scene_id]

    def get_hud(self) -> str:
        p = self.state.player
        return f"HP: [{p.hp}] | Mana: [{p.mana}] | Bullets: [{p.bullet}] | Credits: [{p.credits}]"

    def run_turn(self, player_input: Optional[str] = None):
        """
        Executes one turn of the game.
        Returns: (story_text, event_logs)
        """
        self.context.turn_count += 1
        if self.mode_b_active:
            return self._run_mode_b(player_input), []
        else:
            return self._run_mode_a(player_input)

    def _run_mode_a(self, player_input: Optional[str]):
        """
        Mode A (Guided): Deterministic logic from world.json.
        """
        if player_input:
            try:
                choice_id = int(player_input)
                success = self._select_option(choice_id)
                if not success:
                    return "Invalid choice. Please try again.", []
            except ValueError:
                # Custom Action: Transition to 3-round AI detour
                self.mode_b_active = True
                self.custom_ai_rounds = 3
                return self._run_mode_b(player_input), []

        current_scene = self.get_current_scene()
        
        # Apply deterministic event triggers
        fired_descriptions = self._handle_events()
        
        # Check for AI Takeover trigger (Standard transition)
        if current_scene.id.lower().startswith("end_game_ai") or "ai_takeover" in current_scene.id.lower():
            self.mode_b_active = True
            # For standard AI takeover, we don't necessarily limit rounds unless requested
            # But we'll treat it as a continuous AI mode for now
            return self._run_mode_b(f"The player reached the transition node: {current_scene.text}"), fired_descriptions

        return current_scene.text, fired_descriptions

    def _run_mode_b(self, player_input: Optional[str]):
        """
        Mode B (AI Takeover): Procedural generation with 3-round detour logic.
        """
        # 1. Prepare context for AI
        current_stats = {
            "hp": self.state.player.hp,
            "mana": self.state.player.mana,
            "bullet": self.state.player.bullet,
            "credits": self.state.player.credits
        }
        
        # 2. Re-rail Logic: Identify potential return nodes
        # We look for nodes in the original world graph that are reachable from the point of detour
        # For simplicity, we can pass a few 'Return to Plot' IDs
        available_ids = list(self.state.scenes.keys())
        potential_returns = [sid for sid in available_ids if not sid.startswith("generated_")][:3]
        
        is_re_rail_turn = (self.custom_ai_rounds == 1)
        
        # 3. Call AI Bridge
        ai_scene = call_ai_game_master(
            decision_history=self.memory.history_window,
            current_stats=current_stats,
            decision_number=len(self.memory.history_window),
            last_player_action=player_input,
            is_first_ai_turn=(player_input is None or "reached the transition" in player_input),
            turn_count=self.context.turn_count,
            is_re_rail_turn=is_re_rail_turn,
            re_rail_targets=potential_returns
        )
        
        # 4. Update World State
        self.state.scenes[ai_scene.id] = ai_scene
        self.state.player.current_scene_id = ai_scene.id
        
        # 5. Round Management
        if self.custom_ai_rounds > 0:
            self.custom_ai_rounds -= 1
            if self.custom_ai_rounds == 0:
                self.mode_b_active = False # Re-rail complete
        
        # 6. Persistence
        self.logger.log("AI_GM", ai_scene.text)
        self.memory.add_interaction(player_input or "Transition", ai_scene.text)
        self.memory.save_snapshot(
            self.state.player,
            ai_scene.id,
            self.memory.history_window,
            self.context.turn_count
        )
        
        return ai_scene.text

    def _select_option(self, choice_id: int) -> bool:
        scene = self.get_current_scene()
        selected_option = next((opt for opt in scene.options if opt.id == choice_id), None)

        if selected_option:
            # 1. Log Choice
            self.logger.log("PLAYER", selected_option.text)
            
            # 2. Transition
            self.state.player.current_scene_id = selected_option.next_scene_id
            
            # 3. Update Memory
            self.memory.add_interaction(str(choice_id), selected_option.text)
            self.memory.save_snapshot(
                self.state.player, 
                self.state.player.current_scene_id, 
                self.memory.history_window,
                self.context.turn_count
            )
            return True
        return False

    def _handle_events(self) -> List[str]:
        fired_descriptions = []
        fired_events = self.events.check_triggers(self.state.player.current_scene_id)
        
        for effect_dict, description in fired_events:
            fired_descriptions.append(description)
            self._apply_effect(effect_dict)
            
        return fired_descriptions

    def _apply_effect(self, effect: dict):
        player = self.state.player
        
        # Define stat colors
        colors = {
            "hp": (200, 50, 50),
            "mana": (50, 50, 200),
            "bullet": (200, 200, 50),
            "credits": (50, 200, 50)
        }

        for stat, delta in effect.items():
            if delta != 0:
                old_val = getattr(player, stat, 0)
                setattr(player, stat, old_val + delta)
                
                if self.on_stat_change:
                    prefix = "+" if delta > 0 else ""
                    text = f"{prefix}{delta} {stat.capitalize()}"
                    color = colors.get(stat, (255, 255, 255))
                    self.on_stat_change(text, color)
        
        player.hp = max(0, player.hp)
        player.mana = max(0, player.mana)
        player.bullet = max(0, player.bullet)

    def check_game_over(self) -> Optional[str]:
        if self.state.player.hp <= 0:
            return "SYSTEM FAILURE: Vital signs terminated. Game Over."
        return None

    def run_game(self, ui, bg_path: str):
        """
        The Endless Arcade Loop:
        Restarts the game automatically after an ending is reached.
        """
        while True:
            # 1. Reset everything for a fresh start
            self.reset_game()
            
            # 2. Initial Turn
            output, event_logs = self.run_turn()
            
            while True:
                current_scene = self.get_current_scene()
                
                # 3. Stream narrative text
                ui.stream_scene_text(output, bg_path, [])
                
                # 4. Check for End State
                if current_scene.is_end:
                    # Final display
                    ui.draw_background(bg_path)
                    ui.draw_hud(self.state.player)
                    ui.draw_story_box(output)
                    
                    # Pause so the player/judge can read the ending
                    time.sleep(5)
                    
                    # Break inner loop to restart via the outer loop
                    break
                
                # 5. Handle Choice
                choice_id = ui.get_player_choice(current_scene.options)
                output, event_logs = self.run_turn(choice_id)
