import json
from pathlib import Path
from models import Item, Room, Player, WorldState


def load_tutorial_world(file_path: str = "data/world.json") -> WorldState:
    """Loads the game world state from a JSON file.

    Args:
        file_path (str): The path to the JSON world file.

    Returns:
        WorldState: The initialized game state.
    """
    path = Path(file_path)
    with path.open("r") as f:
        data = json.load(f)

    rooms = {}
    for room_id, room_data in data["rooms"].items():
        items = [
            Item(name=i["name"], description=i["description"])
            for i in room_data.get("items", [])
        ]
        rooms[room_id] = Room(
            name=room_data["name"],
            description=room_data["description"],
            items=items,
            exits=room_data["exits"]
        )

    player = Player(current_room_id=data["initial_room_id"])

    return WorldState(rooms=rooms, player=player)