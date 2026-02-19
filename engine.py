from models import WorldState, Item, Scene, Option
from typing import List, Dict, Any, Optional
import templates
from loader import ThemeLoader
import world
from systems import NarrativeLogger, MemoryManager, EventManager


class GameEngine:
    """The core logic engine for the game (Visual Novel style).

    Handles scene transitions, events, and persistence.
    """

    def __init__(self, theme_name: str):
        """Initializes the engine with a theme and system modules."""
        theme_path = f"assets/themes/{theme_name}"
        loader = ThemeLoader(theme_path)
        
        self.story = loader.load_story()
        self.state = world.load_world_from_theme(loader)
        
        # Systems
        self.logger = NarrativeLogger()
        self.memory = MemoryManager()
        self.events = EventManager()
        self.events.load_triggers(loader.load_events())

        # Log initial scene
        initial_scene = self.get_current_scene()
        self.logger.log("SYSTEM", initial_scene.text)

    def get_current_scene(self) -> Scene:
        """Returns the current scene object."""
        return self.state.scenes[self.state.player.current_scene_id]

    def get_hud(self) -> str:
        """Returns a formatted HUD string."""
        p = self.state.player
        return f"HP: [{p.hp}] | Mana: [{p.mana}] | Bullets: [{p.bullet}] | Credits: [{p.credits}]"

    def handle_events(self) -> List[str]:
        """Checks for and applies scene events.
        
        Returns:
            List[str]: Descriptions of all fired events.
        """
        fired_descriptions = []
        fired_events = self.events.check_triggers(self.state.player.current_scene_id)
        
        for effect_dict, description in fired_events:
            fired_descriptions.append(description)
            self._apply_effect(effect_dict)
            
        return fired_descriptions

    def select_option(self, choice_id: int) -> bool:
        """Validates and applies a choice.
        
        Returns:
            bool: True if selection was successful, False otherwise.
        """
        scene = self.get_current_scene()
        selected_option = next((opt for opt in scene.options if opt.id == choice_id), None)

        if selected_option:
            # 1. Log Choice
            self.logger.log("PLAYER", selected_option.text)
            
            # 2. Transition
            self.state.player.current_scene_id = selected_option.next_scene_id
            new_scene = self.get_current_scene()
            
            # 3. Log New Scene
            self.logger.log("SYSTEM", new_scene.text)
            
            # 4. Update Memory
            self.memory.add_interaction(str(choice_id), selected_option.text)
            self.memory.save_snapshot(
                self.state.player, 
                self.state.player.current_scene_id, 
                self.memory.history_window
            )
            return True
        return False

    def _apply_effect(self, effect: Dict[str, Any]):
        """Applies trigger effects to player state."""
        player = self.state.player
        player.hp += effect.get("hp", 0)
        player.mana += effect.get("mana", 0)
        player.bullet += effect.get("bullet", 0)
        player.credits += effect.get("credits", 0)
        
        # Clamp values
        player.hp = max(0, player.hp)
        player.mana = max(0, player.mana)
        player.bullet = max(0, player.bullet)

    def check_game_over(self) -> Optional[str]:
        """Checks for game over conditions.
        
        Returns:
            Optional[str]: Death message if HP is 0, otherwise None.
        """
        if self.state.player.hp <= 0:
            return "SYSTEM FAILURE: Vital signs terminated. Game Over."
        return None
