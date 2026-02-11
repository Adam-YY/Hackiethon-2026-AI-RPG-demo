from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import random


@dataclass
class EventTrigger:
    """Defines a game logic trigger.

    Attributes:
        event_id (str): Unique identifier for the trigger.
        condition_type (str): The type of event to listen for (e.g., 'location_enter').
        target_id (str): The ID of the room or item that triggers the event.
        action (str): The identifier for the logic to execute when triggered.
        params (Dict[str, Any]): Optional parameters for the action.
    """
    event_id: str
    condition_type: str
    target_id: str
    action: str
    params: Dict[str, Any] = None


def get_weighted_result(choices: Dict[Any, int]) -> Any:
    """Returns a result from a dictionary of weights.

    Args:
        choices (Dict[Any, int]): A mapping of results to their integer weights.

    Returns:
        Any: The selected result.
    """
    results = list(choices.keys())
    weights = list(choices.values())
    return random.choices(results, weights=weights, k=1)[0]


class EventManager:
    """Manages active triggers and event processing."""

    def __init__(self):
        """Initializes the manager with an empty trigger list."""
        self.triggers: List[EventTrigger] = []

    def load_triggers(self, trigger_data: List[Dict[str, Any]]):
        """Loads triggers from a list of dictionaries (usually from JSON).

        Args:
            trigger_data (List[Dict[str, Any]]): The list of raw trigger definitions.
        """
        for t in trigger_data:
            self.triggers.append(EventTrigger(
                event_id=t["event_id"],
                condition_type=t["condition_type"],
                target_id=t["target_id"],
                action=t["action"],
                params=t.get("params", {})
            ))

    def check_triggers(self, event_type: str, context_id: str) -> List[EventTrigger]:
        """Checks if any triggers match the current event and context.

        Args:
            event_type (str): The type of event (e.g., 'ROOM_ENTER').
            context_id (str): The ID of the entity involved (e.g., room_id).

        Returns:
            List[EventTrigger]: A list of triggered events to be processed.
        """
        fired_triggers = []
        for trigger in self.triggers:
            if trigger.condition_type == event_type and trigger.target_id == context_id:
                fired_triggers.append(trigger)
        return fired_triggers
