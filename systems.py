import json
import time
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from models import WorldState, Player


@dataclass
class Trigger:
    """Defines a deterministic or probabilistic game event.

    Attributes:
        event_id (str): Unique identifier for the trigger.
        trigger_type (str): Type of event (e.g., 'scene_enter').
        condition (str): The scene_id that triggers the event.
        probability (float): Chance of the event firing (0.0 to 1.0).
        narrative_description (str): Text to display when triggered.
        result (Dict[str, Any]): State changes (e.g., {'hp': -5}).
    """
    event_id: str
    trigger_type: str
    condition: str
    probability: float
    narrative_description: str
    result: Dict[str, Any] = field(default_factory=dict)


class EventManager:
    """Manages event triggers and executes their effects on the game state."""

    def __init__(self):
        self.triggers: List[Trigger] = []

    def load_triggers(self, trigger_data: List[Dict[str, Any]]):
        """Loads trigger definitions from raw data."""
        self.triggers = []
        for data in trigger_data:
            self.triggers.append(Trigger(
                event_id=data["event_id"],
                trigger_type=data["trigger_type"],
                condition=data["condition"],
                probability=data.get("probability", 1.0),
                narrative_description=data["narrative_description"],
                result=data.get("result", {})
            ))

    def check_triggers(self, scene_id: str) -> List[Tuple[Dict[str, Any], str]]:
        """Checks for matching triggers for a specific scene.

        Returns:
            List[Tuple[Dict[str, Any], str]]: A list of (result, description) for fired events.
        """
        fired_events = []
        for t in self.triggers:
            if t.condition == scene_id:
                if random.random() <= t.probability:
                    fired_events.append((t.result, t.narrative_description))
        return fired_events


class NarrativeLogger:
    """Handles human-readable session logging."""

    def __init__(self, log_dir: str = "logs"):
        """Initializes the logger and creates a new session file.

        Args:
            log_dir (str): Directory where logs will be stored.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.file_path = self.log_dir / f"session_{timestamp}.txt"
        
        # Ensure the file is created
        self.file_path.touch()

    def log(self, role: str, text: str):
        """Appends a line to the narrative log and flushes the buffer.

        Args:
            role (str): The entity speaking/acting (e.g., 'PLAYER', 'SYSTEM').
            text (str): The content to log.
        """
        if role.upper() == "PLAYER":
            entry = f"Selected Option: {text}\n"
        else:
            entry = f"Scene Description: {text.strip()}\n"
        
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(entry)
            f.flush()
            os.fsync(f.fileno())

    def reset_game(self):
        """Wipes the current session log file."""
        with self.file_path.open("w", encoding="utf-8") as f:
            f.truncate(0)


class MemoryManager:
    """Handles machine-readable state snapshots and interaction history."""

    def __init__(self, save_path: str = "saves/memory.json"):
        """Initializes the memory manager.

        Args:
            save_path (str): Path to the JSON snapshot file.
        """
        self.save_path = Path(save_path)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_window: List[Dict[str, str]] = []

    def add_interaction(self, user_input: str, game_response: str):
        """Adds an interaction to the sliding window (max 5).

        Args:
            user_input (str): The player's command.
            game_response (str): The engine's reply.
        """
        self.history_window.append({
            "action": user_input,
            "result": game_response.strip()
        })
        
        if len(self.history_window) > 5:
            self.history_window.pop(0)

    def reset_game(self):
        """Clears interaction history and wipes the memory.json file."""
        self.history_window = []
        if self.save_path.exists():
            with self.save_path.open("w", encoding="utf-8") as f:
                json.dump({}, f)

    def save_snapshot(self, player: Player, current_scene_id: str, recent_history: List[Dict[str, str]], turn_count: int = 0):
        """Saves a compressed memory.json for AI consumption.

        Args:
            player (Player): The player object.
            current_scene_id (str): The ID of the current scene.
            recent_history (List[Dict[str, str]]): Recent interaction history.
            turn_count (int): The current turn number.
        """
        compressed_memory = {
            "player_state": {
                "hp": player.hp,
                "mana": player.mana,
                "bullet": player.bullet,
                "credits": player.credits,
                "inventory": [item.name for item in player.inventory]
            },
            "current_location": current_scene_id,
            "recent_history": recent_history,
            "turn_count": turn_count,
            "timestamp": time.time()
        }

        with self.save_path.open("w", encoding="utf-8") as f:
            json.dump(compressed_memory, f, indent=2)

    def save_context(self, state: WorldState):
        """Saves a compressed memory.json for AI consumption (Legacy/Internal)."""
        self.save_snapshot(state.player, state.player.current_scene_id, self.history_window, 0)

    def save_full_snapshot(self, state: WorldState):
        """Serializes current full state and history window to JSON.

        Args:
            state (WorldState): The current game world state.
        """
        snapshot_path = self.save_path.parent / "state_snapshot.json"
        snapshot = {
            "state": state.to_dict(),
            "history_window": self.history_window,
            "timestamp": time.time()
        }
        
        with snapshot_path.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
