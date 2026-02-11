import json
import time
import os
from pathlib import Path
from typing import List, Dict, Any
from models import WorldState


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
            role (str): The entity speaking/acting (e.g., 'PLAYER', 'GAME').
            text (str): The content to log.
        """
        prefix = f"[{role.upper()}]: " if role.lower() == "game" else f"{role.lower()}: "
        entry = f"{prefix}{text}\n"
        
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
            "input": user_input,
            "output": game_response.strip()
        })
        
        if len(self.history_window) > 10:
            self.history_window.pop(0)

    def save_snapshot(self, state: WorldState):
        """Serializes current state and history window to JSON.

        Args:
            state (WorldState): The current game world state.
        """
        snapshot = {
            "state": state.to_dict(),
            "history_window": self.history_window,
            "timestamp": time.time()
        }
        
        with self.save_path.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
