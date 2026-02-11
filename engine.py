from models import WorldState, Item
from typing import List


class GameEngine:
    """The core logic engine for the game.

    Handles state transitions based on player commands.

    Attributes:
        state (WorldState): The current state of the game world.
    """

    def __init__(self, state: WorldState):
        """Initializes the engine with a world state.

        Args:
            state (WorldState): The initial game world state.
        """
        self.state = state

    def process_command(self, command: str) -> str:
        """Processes a player command and updates the world state.

        Args:
            command (str): The raw input string from the player.

        Returns:
            str: The result of the command to be displayed to the player.
        """
        tokens = command.lower().strip().split()
        if not tokens:
            return "Enter a command."

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
                return f"I don't understand '{command}'."

    def _move(self, direction: str) -> str:
        """Attempts to move the player in a given direction.

        Args:
            direction (str): The direction to move.

        Returns:
            str: A description of the move or an error message.
        """
        player = self.state.player
        current_room = self.state.rooms[player.current_room_id]

        if direction in current_room.exits:
            new_room_id = current_room.exits[direction]
            player.current_room_id = new_room_id
            new_room = self.state.rooms[new_room_id]
            return f"You move {direction} to the {new_room.name}.\n\n{new_room.description}"
        else:
            return f"You cannot go {direction} from here."

    def _look(self) -> str:
        """Describes the current room, its items, and exits.

        Returns:
            str: The room description.
        """
        room = self.state.rooms[self.state.player.current_room_id]
        desc = f"{room.name}\n{room.description}\n"
        
        if room.items:
            item_names = [item.name for item in room.items]
            desc += f"\nYou see: {', '.join(item_names)}"
        
        exits = ", ".join(room.exits.keys())
        desc += f"\nExits: {exits}"
        
        return desc

    def _take(self, item_name: str) -> str:
        """Attempts to pick up an item from the current room.

        Args:
            item_name (str): The name of the item to take.

        Returns:
            str: A message indicating success or failure.
        """
        room = self.state.rooms[self.state.player.current_room_id]
        
        for item in room.items:
            if item.name.lower() == item_name.lower():
                room.items.remove(item)
                self.state.player.inventory.append(item)
                return f"You take the {item.name}."
        
        return f"There is no '{item_name}' here."

    def _inventory(self) -> str:
        """Lists the items in the player's inventory.

        Returns:
            str: The inventory list.
        """
        if not self.state.player.inventory:
            return "Your inventory is empty."
        
        item_names = [item.name for item in self.state.player.inventory]
        return f"You are carrying: {', '.join(item_names)}"
