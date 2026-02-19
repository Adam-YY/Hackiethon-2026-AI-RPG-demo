from models import WorldState, Item
from typing import List, Dict, Any, Optional
import templates
from loader import ThemeLoader
import world
from systems import NarrativeLogger, MemoryManager, EventManager


class GameEngine:
    """The core logic engine for the game.

    Handles FSM states, event triggers, and persistence.

    Attributes:
        state (WorldState): The current state of the game world.
        mode (str): Current FSM mode ('EXPLORATION', 'COMBAT', 'MENU').
    """

    def __init__(self, theme_name: str):
        """Initializes the engine with a theme and system modules.

        Args:
            theme_name (str): The name of the theme folder in assets/themes/.
        """
        theme_path = f"assets/themes/{theme_name}"
        loader = ThemeLoader(theme_path)
        
        self.story = loader.load_story()
        self.state = world.load_world_from_theme(loader)
        self.mode = "EXPLORATION"
        
        # Systems
        self.logger = NarrativeLogger()
        self.memory = MemoryManager()
        self.events = EventManager()
        self.events.load_triggers(loader.load_events())

        # Print Intro Text
        print(f"\n--- {self.story.get('title', 'Unknown Title')} "
              f"---")
        print(f"{self.story.get('intro_text', 'No intro text '
                                              'available.')}\n")

    def process_command(self, command: str) -> str:
        """Processes a player command, logs interactions, and saves state.

        Args:
            command (str): The raw input string from the player.

        Returns:
            str: The result of the command.
        """
        self.logger.log("PLAYER", command)
        
        response = ""
        match self.mode:
            case "EXPLORATION":
                response = self._handle_exploration(command)
            case _:
                response = f"Mode '{self.mode}' not implemented."

        # Check for events triggered by the last action (if any)
        # Note: Triggers are specifically checked within action methods like _move
        
        self.logger.log("SYSTEM", response)
        self.memory.add_interaction(command, response)
        self.memory.save_context(self.state)
        self.memory.save_snapshot(self.state)
        
        return response

    def _handle_exploration(self, command: str) -> str:
        """Logic for the Exploration FSM state."""
        tokens = command.lower().strip().split()
        if not tokens:
            return templates.ERROR_NO_INPUT

        match tokens:
            case ["move", direction] | ["go", direction]:
                return self._move(direction)
            case ["look"]:
                return self._look()
            case ["take", *item_parts]:
                return self._take(" ".join(item_parts))
            case ["inventory"] | ["i"]:
                return self._inventory()
            case ["stats"] | ["status"]:
                return self._stats()
            case _:
                return templates.ERROR_UNKNOWN.format(command=command)

    def _move(self, direction: str) -> str:
        """Moves player and checks for enter_room triggers."""
        player = self.state.player
        current_room = self.state.rooms[player.current_room_id]

        if direction in current_room.exits:
            new_room_id = current_room.exits[direction]
            player.current_room_id = new_room_id
            new_room = self.state.rooms[new_room_id]
            
            result = templates.MOVE_SUCCESS.format(
                direction=direction,
                room_name=new_room.name,
                description=new_room.description
            )

            # Check for events
            triggers = self.events.check_triggers("enter_room", new_room_id)
            for trigger in triggers:
                result += f"\n\n[EVENT]: {trigger.narrative_description}"
                self._apply_effect(trigger.result_effect)
            
            return result
        else:
            return templates.MOVE_FAIL.format(direction=direction)

    def _take(self, item_name: str) -> str:
        """Takes an item and checks for take_item triggers."""
        room = self.state.rooms[self.state.player.current_room_id]
        for item in room.items:
            if item.name.lower() == item_name.lower():
                room.items.remove(item)
                self.state.player.inventory.append(item)
                
                result = templates.TAKE_SUCCESS.format(item_name=item.name)
                
                # Check for events
                triggers = self.events.check_triggers("take_item", item.name)
                for trigger in triggers:
                    result += f"\n\n[EVENT]: {trigger.narrative_description}"
                    self._apply_effect(trigger.result_effect)
                
                return result
        return templates.TAKE_FAIL.format(item_name=item_name)

    def _apply_effect(self, effect: Dict[str, Any]):
        """Applies trigger effects to player state."""
        player = self.state.player
        player.hp += effect.get("hp", 0)
        player.mana += effect.get("mana", 0)
        player.bullet += effect.get("bullet", 0)
        player.credits += effect.get("credits", 0)
        player.hp = max(0, player.hp)
        player.mana = max(0, player.mana)
        player.bullet = max(0, player.bullet)

    def _stats(self) -> str:
        """Returns the player's current status."""
        p = self.state.player
        return f"STATUS: HP: {p.hp} | Mana: {p.mana} | Bullets: {p.bullet} | Credits: {p.credits} | Inv: {len(p.inventory)} items"

    def get_hud_data(self) -> Dict[str, Any]:
        """Returns data for the HUD."""
        p = self.state.player
        room = self.state.rooms[p.current_room_id]
        return {
            "hp": p.hp,
            "mana": p.mana,
            "bullet": p.bullet,
            "credits": p.credits,
            "room_name": room.name
        }

    def check_win_condition(self) -> Optional[str]:
        """Checks if the player has met the winning condition.
        
        For this version, we check if the player reached the target room 
        defined in the story or a hardcoded 'penthouse' for cyberpunk.
        """
        player = self.state.player
        if player.current_room_id == "penthouse":
            return self.story.get("winning_condition", "You won!")
        
        if player.hp <= 0:
            return "SYSTEM FAILURE: Vital signs terminated. Game Over."
            
        return None

    def _look(self) -> str:
        room = self.state.rooms[self.state.player.current_room_id]
        desc = templates.LOOK_ROOM_DESC.format(
            room_name=room.name,
            room_description=room.description
        )
        if room.items:
            item_list = ", ".join(item.name for item in room.items)
            desc += templates.LOOK_ITEMS.format(item_list=item_list)
        exit_list = ", ".join(room.exits.keys())
        desc += templates.LOOK_EXITS.format(exit_list=exit_list)
        return desc

    def _inventory(self) -> str:
        if not self.state.player.inventory:
            return templates.INVENTORY_EMPTY
        item_list = ", ".join(item.name for item in self.state.player.inventory)
        return templates.INVENTORY_LIST.format(item_list=item_list)
