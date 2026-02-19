import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from models import WorldState, Scene, Option, Item, Player


class ThemeLoader:
    """Handles loading and validation of game themes from JSON files."""

    def __init__(self, theme_path: str):
        """Initializes the loader with a specific theme directory.

        Args:
            theme_path (str): Path to the theme folder (e.g., 'assets/themes/WasteLand').
        """
        self.theme_path = Path(theme_path)
        self.world_file = self.theme_path / "world.json"

    def load_world(self) -> WorldState:
        """Parses world.json and returns an initialized WorldState.

        Returns:
            WorldState: The validated world state.

        Raises:
            FileNotFoundError: If world.json is missing.
            ValueError: If the JSON is malformed or contains invalid scene references.
        """
        if not self.world_file.exists():
            raise FileNotFoundError(f"Missing required world file: {self.world_file}")

        with self.world_file.open("r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON in {self.world_file}: {e}")

        # 1. Parse Scenes
        scenes: Dict[str, Scene] = {}
        for scene_id, scene_data in data.get("scenes", {}).items():
            options = [
                Option(
                    id=opt.get("id"),
                    text=opt.get("text"),
                    next_scene_id=opt.get("next_scene_id")
                )
                for opt in scene_data.get("options", [])
            ]
            scenes[scene_id] = Scene(
                id=scene_id,
                text=scene_data.get("text", ""),
                is_end=scene_data.get("is_end", False),
                options=options
            )

        # 2. Validation: Check if all next_scene_id exist
        for scene_id, scene in scenes.items():
            for option in scene.options:
                if option.next_scene_id not in scenes:
                    raise ValueError(
                        f"Validation Error: Scene '{scene_id}' has an option '{option.id}' "
                        f"leading to non-existent scene '{option.next_scene_id}'."
                    )

        # 3. Validation: Initial scene check
        initial_id = data.get("initial_scene_id")
        if not initial_id or initial_id not in scenes:
            raise ValueError(f"Invalid or missing initial_scene_id: '{initial_id}'")

        # 4. Initialize Player
        player_data = data.get("player", {})
        player = Player(
            current_scene_id=initial_id,
            hp=player_data.get("hp", 100),
            mana=player_data.get("mana", 50),
            bullet=player_data.get("bullet", 5),
            credits=player_data.get("credits", 50)
        )

        return WorldState(scenes=scenes, player=player)

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
            try:
                data = json.load(f)
                return data.get("triggers", [])
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON in {events_file}: {e}")
