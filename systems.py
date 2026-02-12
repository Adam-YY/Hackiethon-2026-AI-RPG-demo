import json
import time
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models import WorldState


@dataclass
class Trigger:
    """Defines a deterministic or probabilistic game event.

    Attributes:
        event_id (str): Unique identifier for the trigger.
        trigger_type (str): Type of event (e.g., 'enter_room', 'take_item').
        condition (str): The ID of the room or item that triggers the event.
        probability (float): Chance of the event firing (0.0 to 1.0).
        narrative_description (str): Text to display when triggered.
        result_effect (Dict[str, Any]): State changes (e.g., {'hp': -5}).
    """
    event_id: str
    trigger_type: str
    condition: str
    probability: float
    narrative_description: str
    result_effect: Dict[str, Any] = field(default_factory=dict)


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
                result_effect=data.get("result_effect", {})
            ))

    def check_triggers(self, trigger_type: str, condition: str) -> List[Trigger]:
        """Checks for matching triggers and handles probability."""
        fired = []
        for t in self.triggers:
            if t.trigger_type == trigger_type and t.condition == condition:
                if random.random() <= t.probability:
                    fired.append(t)
        return fired


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
            entry = f"Player: {text} -> "
        else:
            entry = f"System: {text.strip()}\n"
        
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(entry)
            f.flush()
            os.fsync(f.fileno())


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
        """Adds an interaction to the sliding window (max 10).

        Args:
            user_input (str): The player's command.
            game_response (str): The engine's reply.
        """
        self.history_window.append({
            "action": user_input,
            "result": game_response.strip()
        })
        
        if len(self.history_window) > 10:
            self.history_window.pop(0)

    def save_context(self, state: WorldState):
        """Saves a compressed memory.json for AI consumption.

        Args:
            state (WorldState): The current game world state.
        """
        player = state.player
        current_room = state.rooms[player.current_room_id]
        
        compressed_memory = {
            "current_stats": {
                "hp": player.hp,
                "credits": player.credits,
                "inventory": [item.name for item in player.inventory]
            },
            "immediate_surroundings": {
                "room_name": current_room.name,
                "description": current_room.description,
                "exits": list(current_room.exits.keys()),
                "items_present": [item.name for item in current_room.items]
            },
            "last_5_actions": self.history_window[-5:]
        }

        with self.save_path.open("w", encoding="utf-8") as f:
            json.dump(compressed_memory, f, indent=2)

    def save_snapshot(self, state: WorldState):
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
