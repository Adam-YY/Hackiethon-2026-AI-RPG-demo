from models import WorldState, Item
from typing import List, Dict, Any
import templates
from loader import ThemeLoader
import world
from history import NarrativeLogger, MemoryManager
from events import EventManager, get_weighted_result


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
        print(f"\n--- {self.story.get('title', 'Unknown Title')} ---")
        print(f"{self.story.get('intro_text', 'No intro text available.')}\n")

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
        
        self.logger.log("GAME", response)
        self.memory.add_interaction(command, response)
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
            case _:
                return templates.ERROR_UNKNOWN.format(command=command)

    def _move(self, direction: str) -> str:
        """Moves player and checks for ROOM_ENTER triggers."""
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
            triggers = self.events.check_triggers("ROOM_ENTER", new_room_id)
            for trigger in triggers:
                trigger_msg = self._execute_trigger(trigger)
                if trigger_msg:
                    result += f"\n\n{trigger_msg}"
            
            return result
        else:
            return templates.MOVE_FAIL.format(direction=direction)

    def _execute_trigger(self, trigger: Any) -> str:
        """Executes the action associated with a trigger."""
        match trigger.action:
            case "MESSAGE":
                return trigger.params.get("text", "")
            case "ENCOUNTER":
                table = trigger.params.get("table", {})
                result = get_weighted_result(table)
                if result != "nothing":
                    return f"[ENCOUNTER]: A {result} appears!"
                return ""
            case _:
                return ""

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

    def _take(self, item_name: str) -> str:
        room = self.state.rooms[self.state.player.current_room_id]
        for item in room.items:
            if item.name.lower() == item_name.lower():
                room.items.remove(item)
                self.state.player.inventory.append(item)
                return templates.TAKE_SUCCESS.format(item_name=item.name)
        return templates.TAKE_FAIL.format(item_name=item_name)

    def _inventory(self) -> str:
        if not self.state.player.inventory:
            return templates.INVENTORY_EMPTY
        item_list = ", ".join(item.name for item in self.state.player.inventory)
        return templates.INVENTORY_LIST.format(item_list=item_list)
