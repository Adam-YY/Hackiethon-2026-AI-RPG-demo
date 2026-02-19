import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from models import WorldState, Room, Item, Player


class ThemeLoader:
    """Handles loading and validation of game themes from JSON files."""

    def __init__(self, theme_path: str):
        """Initializes the loader with a specific theme directory.

        Args:
            theme_path (str): Path to the theme folder (e.g., 'assets/themes/default').
        """
        self.theme_path = Path(theme_path)
        self.world_file = self.theme_path / "world.json"

    def load_world(self) -> WorldState:
        """Parses world.json and returns an initialized WorldState.

        Returns:
            WorldState: The validated world state.

        Raises:
            FileNotFoundError: If world.json is missing.
            ValueError: If the JSON is malformed or contains invalid room references.
        """
        if not self.world_file.exists():
            raise FileNotFoundError(f"Missing required world file: {self.world_file}")

        with self.world_file.open("r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON in {self.world_file}: {e}")

        # 1. Parse Rooms and Items
        rooms: Dict[str, Room] = {}
        for room_id, room_data in data.get("rooms", {}).items():
            items = [
                Item(name=i["name"], description=i["description"])
                for i in room_data.get("items", [])
            ]
            rooms[room_id] = Room(
                name=room_data["name"],
                description=room_data["description"],
                items=items,
                exits=room_data.get("exits", {})
            )

        # 2. Validation: Check if all exit room_ids exist
        for room_id, room in rooms.items():
            for direction, target_id in room.exits.items():
                if target_id not in rooms:
                    raise ValueError(
                        f"Validation Error: Room '{room_id}' has exit '{direction}' "
                        f"leading to non-existent room '{target_id}'."
                    )

        # 3. Validation: Initial room check
        initial_id = data.get("initial_room_id")
        if not initial_id or initial_id not in rooms:
            raise ValueError(f"Invalid or missing initial_room_id: '{initial_id}'")

        # 4. Initialize Player
        player_data = data.get("player", {})
        player = Player(
            current_room_id=initial_id,
            hp=player_data.get("hp", 100),
            mana=player_data.get("mana", 50),
            bullet=player_data.get("bullet", 5),
            credits=player_data.get("credits", 50)
        )

        return WorldState(rooms=rooms, player=player)

    def load_story(self) -> Dict[str, str]:
        """Parses story.json from the theme folder.

        Returns:
            Dict[str, str]: Story data (title, intro_text, etc.).
        """
        story_file = self.theme_path / "story.json"
        if not story_file.exists():
            return {
                "title": "A New Adventure",
                "intro_text": "You stand at the beginning of a mysterious journey...",
                "winning_condition": "Unknown"
            }

        with story_file.open("r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON in {story_file}: {e}")

    def load_events(self) -> List[Dict[str, Any]]:
        """Parses events.json from the theme folder.

        Returns:
            List[Dict[str, Any]]: A list of raw trigger definitions.
        """
        events_file = self.theme_path / "events.json"
        if not events_file.exists():
            return []

        with events_file.open("r") as f:
            data = json.load(f)
            return data.get("triggers", [])
