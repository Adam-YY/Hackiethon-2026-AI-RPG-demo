from models import WorldState, Item
from typing import List
import templates


class GameEngine:
    """The core logic engine for the game.

    Handles state transitions based on player commands using templates for feedback.

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
            return templates.MOVE_SUCCESS.format(
                direction=direction,
                room_name=new_room.name,
                description=new_room.description
            )
        else:
            return templates.MOVE_FAIL.format(direction=direction)

    def _look(self) -> str:
        """Describes the current room, its items, and exits.

        Returns:
            str: The room description.
        """
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
                return templates.TAKE_SUCCESS.format(item_name=item.name)
        
        return templates.TAKE_FAIL.format(item_name=item_name)

    def _inventory(self) -> str:
        """Lists the items in the player's inventory.

        Returns:
            str: The inventory list.
        """
        if not self.state.player.inventory:
            return templates.INVENTORY_EMPTY
        
        item_list = ", ".join(item.name for item in self.state.player.inventory)
        return templates.INVENTORY_LIST.format(item_list=item_list)