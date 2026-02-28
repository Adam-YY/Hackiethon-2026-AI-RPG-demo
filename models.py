from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class Option:
    """A choice available in a scene.

    Attributes:
        id (int): The unique identifier for the option.
        text (str): The narrative text of the choice.
        next_scene_id (str): The ID of the scene this choice leads to.
    """
    id: int
    text: str
    next_scene_id: str


@dataclass
class Scene:
    """A narrative node in the game world (Visual Novel style).

    Attributes:
        id (str): Unique identifier for the scene.
        text (str): The narrative text of the scene.
        is_end (bool): Whether this scene is a terminal node.
        options (List[Option]): A list of choices available to the player.
    """
    id: str
    text: str
    is_end: bool = False
    options: List[Option] = field(default_factory=list)


@dataclass
class Item:
    """An item that can be picked up or used in the game."""
    name: str
    description: str


@dataclass
class Player:
    """The player character and their current state.

    Attributes:
        current_scene_id (str): The ID of the scene where the player is located.
        inventory (List[Item]): A list of items carried by the player.
        hp (int): Health points of the player.
        mana (int): Mana points of the player.
        bullet (int): Number of bullets the player has.
        credits (int): Currency owned by the player.
    """
    current_scene_id: str
    inventory: List[Item] = field(default_factory=list)
    hp: int = 100
    mana: int = 50
    bullet: int = 5
    credits: int = 50

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorldState:
    """The isolated state of the game world.

    Attributes:
        scenes (Dict[str, Scene]): A mapping of scene IDs to Scene objects.
        player (Player): The player object.
    """
    scenes: Dict[str, Scene]
    player: Player

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GameContext:
    """Tracks global session-specific state.

    Attributes:
        turn_count (int): The number of turns elapsed in the current session.
    """
    turn_count: int = 0
