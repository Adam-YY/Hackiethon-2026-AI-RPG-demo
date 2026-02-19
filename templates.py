"""Templates for engine responses to ensure consistent and easily modifiable feedback."""

SCENE_DESC = "{text}\n"
OPTION_LIST = "\nChoices:\n{options}"
OPTION_FORMAT = "{id}. {text}"

MOVE_SUCCESS = "Selected: {choice_text}\n"
MOVE_FAIL = "Invalid choice: {choice_id}."

ERROR_NO_INPUT = "Enter a command or choice number."
ERROR_UNKNOWN = "I don't understand '{command}'."

INVENTORY_EMPTY = "Your inventory is empty."
INVENTORY_LIST = "You are carrying: {item_list}"

LOOK_ITEMS = "\nYou see: {item_list}"
