"""Templates for engine responses to ensure consistent and easily modifiable feedback."""

MOVE_SUCCESS = "You move {direction} to the {room_name}.\n\n{description}"
MOVE_FAIL = "You cannot go {direction} from here."

LOOK_ROOM_DESC = "{room_name}\n{room_description}\n"
LOOK_ITEMS = "\nYou see: {item_list}"
LOOK_EXITS = "\nExits: {exit_list}"

TAKE_SUCCESS = "You take the {item_name}."
TAKE_FAIL = "There is no '{item_name}' here."

INVENTORY_EMPTY = "Your inventory is empty."
INVENTORY_LIST = "You are carrying: {item_list}"

ERROR_NO_INPUT = "Enter a command."
ERROR_UNKNOWN = "I don't understand '{command}'."
