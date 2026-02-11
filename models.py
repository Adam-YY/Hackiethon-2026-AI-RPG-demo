from dataclasses import dataclass, field, asdict
from typing import List, Dict


@dataclass
class Entity:
    """Base class for anything with a name and description.

    Attributes:
        name (str): The name of the entity.
        description (str): A detailed description of the entity.
    """
    name: str
    description: str

    def to_dict(self) -> dict:
        """Converts the entity to a dictionary.

        Returns:
            dict: The dictionary representation of the entity.
        """
        return asdict(self)


@dataclass
class Item(Entity):
    """An item that can be picked up or used in the game.

    Inherits from Entity.
    """
    pass


@dataclass
class Room(Entity):
    """A graph node representing a location in the game world.

    Attributes:
        items (List[Item]): A list of items currently in the room.
        exits (Dict[str, str]): A mapping of directions to room IDs.
    """
    items: List[Item] = field(default_factory=list)
    exits: Dict[str, str] = field(default_factory=dict)


@dataclass
class Player:
    """The player character and their current state.

    Attributes:
        current_room_id (str): The ID of the room where the player is located.
        inventory (List[Item]): A list of items carried by the player.
    """
    current_room_id: str
    inventory: List[Item] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Converts the player to a dictionary.

        Returns:
            dict: The dictionary representation of the player.
        """
        return asdict(self)


@dataclass
class WorldState:
    """The isolated state of the game world.

    Attributes:
        rooms (Dict[str, Room]): A mapping of room IDs to Room objects.
        player (Player): The player object.
    """
    rooms: Dict[str, Room]
    player: Player

    def to_dict(self) -> dict:
        """Converts the world state to a dictionary.

        Returns:
            dict: The dictionary representation of the world state.
        """
        return asdict(self)
