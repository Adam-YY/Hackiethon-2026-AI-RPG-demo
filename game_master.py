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

        # Global Pacing
        self.global_turn_count = 0
        self.max_turns = 20

        # AI Control
        self.in_dynamic_mode = False
        self.saved_target_scene_id: Optional[str] = None
        self.target_scene_text: Optional[str] = None

        # Callbacks
        self.on_stat_change = on_stat_change

    def reset_game(self, theme_name: str = "WasteLand"):
        """Resets the game state, memory, and logs for a new player."""
        theme_path = f"assets/themes/{theme_name}"
        loader = ThemeLoader(theme_path)
        
        self.state = world.load_world_from_theme(loader)
        self.memory.reset_game()
        self.logger.reset_game()
        
        self.global_turn_count = 0
        self.in_dynamic_mode = False
        self.saved_target_scene_id = None
        self.target_scene_text = None

    def get_current_scene(self) -> Scene:
        return self.state.scenes[self.state.player.current_scene_id]

    def get_hud(self) -> str:
        p = self.state.player
        return f"HP: [{p.hp}] | Mana: [{p.mana}] | Bullets: [{p.bullet}] | Credits: [{p.credits}]"

    def run_turn(self, player_input: Optional[str] = None):
        """
        Executes one turn of the game.
        Increments the global turn budget and handles transitions.
        """
        self.global_turn_count += 1
        
        # 1. Process choice if provided (Updates current_scene_id)
        if player_input:
            try:
                choice_id = int(player_input)
                # If selection fails, it's either an invalid ID or we are in Mode B
                # where current_scene_id might not exist yet.
                self._select_option(choice_id)
            except ValueError:
                # Custom Action submitted
                if not self.in_dynamic_mode:
                    current_scene = self.get_current_scene()
                    self.saved_target_scene_id = current_scene.id
                    self.target_scene_text = current_scene.text
                    self.in_dynamic_mode = True
                return self._run_mode_b(player_input), []

        # 2. Determine which mode to run for narrative generation
        if self.in_dynamic_mode:
            return self._run_mode_b(player_input), []
        else:
            return self._run_mode_a(player_input)

    def _run_mode_a(self, player_input: Optional[str]):
        """
        Mode A (Guided): Deterministic logic from world.json.
        """
        # Post-Transition logic
        current_scene = self.get_current_scene()
        
        # Check turn limit: Force AI Climax if limit reached
        if self.global_turn_count >= self.max_turns and not current_scene.is_end:
            self.in_dynamic_mode = True
            self.target_scene_text = "The story reaches its final conclusion."
            self.saved_target_scene_id = current_scene.id
            return self._run_mode_b("The temporal distortion forces an ending."), []

        # Apply deterministic event triggers
        fired_descriptions = self._handle_events()
        
        # Check for hardcoded AI takeover nodes
        if current_scene.id.lower().startswith("end_game_ai") or "ai_takeover" in current_scene.id.lower():
            self.in_dynamic_mode = True
            # Transition to Mode B immediately
            return self._run_mode_b(f"The player reached the transition node: {current_scene.text}"), fired_descriptions

        return current_scene.text, fired_descriptions

    def _run_mode_b(self, player_input: Optional[str]):
        """
        Mode B (AI Takeover): Infinite Dynamic State with Semantic Re-entry.
        """
        # 1. Prepare context for AI
        current_stats = {
            "hp": self.state.player.hp,
            "mana": self.state.player.mana,
            "bullet": self.state.player.bullet,
            "credits": self.state.player.credits
        }
        
        # 2. Call AI Bridge
        ai_scene = call_ai_game_master(
            decision_history=self.memory.history_window,
            current_stats=current_stats,
            decision_number=len(self.memory.history_window),
            last_player_action=player_input,
            is_first_ai_turn=(player_input is None or "reached the transition" in player_input),
            turn_count=self.global_turn_count,
            max_turns=self.max_turns,
            target_scene_text=self.target_scene_text,
            target_scene_id=self.saved_target_scene_id
        )
        
        # 3. Handle the AI's JSON Response
        
        # Hard Safety: Force conclusion if turn budget is exhausted
        if self.global_turn_count >= self.max_turns:
            ai_scene.is_end = True
            ai_scene.options = []

        # Apply AI-generated stat consequences
        if hasattr(ai_scene, "stat_changes") and ai_scene.stat_changes:
            self._apply_effect(ai_scene.stat_changes)

        if ai_scene.is_end:
            # The interface loop will detect current_scene.is_end and stop.
            pass
            
        elif ai_scene.reached_target_plot:
            # Semantic Re-entry: Point the generated options back to our world.json target
            for opt in ai_scene.options:
                opt.next_scene_id = self.saved_target_scene_id
            
            # Deactivate dynamic mode so the next turn starts back in Mode A
            self.in_dynamic_mode = False
        
        else:
            # Sandbox Continue: Ensure 'dynamic_await' never leaks into the scene IDs
            for opt in ai_scene.options:
                if opt.next_scene_id == "dynamic_await":
                    # We'll set it to a special ID that run_turn knows to handle via Mode B
                    opt.next_scene_id = "ai_sandbox_node"

        # 4. Update World State (Generate a temporary Scene node)
        self.state.scenes[ai_scene.id] = ai_scene
        self.state.player.current_scene_id = ai_scene.id
        
        # 5. Persistence
        self.logger.log("AI_GM", ai_scene.text)
        self.memory.add_interaction(player_input or "Transition", ai_scene.text)
        self.memory.save_snapshot(
            self.state.player,
            ai_scene.id,
            self.memory.history_window,
            self.global_turn_count
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
                self.global_turn_count
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
        """Applies stat changes with boundary checks and triggers UI feedback."""
        player = self.state.player
        
        # Define stat colors for UI notifications
        colors = {
            "hp": (200, 50, 50),
            "mana": (50, 50, 200),
            "bullet": (200, 200, 50),
            "credits": (50, 200, 50)
        }

        for stat, delta in effect.items():
            if delta != 0:
                old_val = getattr(player, stat, 0)
                new_val = old_val + delta
                
                # Apply Stat Boundaries
                if stat == "hp":
                    new_val = max(0, min(100, new_val))
                else:
                    new_val = max(0, new_val) # Other stats don't necessarily have an upper cap here
                
                setattr(player, stat, new_val)
                
                # Trigger floating UI notification if a callback is registered
                if self.on_stat_change:
                    prefix = "+" if delta > 0 else ""
                    text = f"{prefix}{delta} {stat.capitalize()}"
                    color = colors.get(stat, (255, 255, 255))
                    self.on_stat_change(text, color)

    def check_game_over(self) -> Optional[str]:
        if self.state.player.hp <= 0:
            return "SYSTEM FAILURE: Vital signs terminated. Game Over."
        return None
