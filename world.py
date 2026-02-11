from models import Item, Room, Player, WorldState


def load_tutorial_world() -> WorldState:
    """Manually instantiates the initial game world state.

    Creates a 3-room world with a Start Room, Hallway, and Observation Deck,
    including the initial items and player position.

    Returns:
        WorldState: The initialized game state.
    """
    # Define Items
    scalpel = Item(
        name="Rusty Scalpel",
        description="A jagged, blood-stained surgical tool. It looks like it "
                    "hasn't been cleaned in decades."
    )

    # Define Rooms
    cryo_chamber = Room(
        name="Cryo-Chamber",
        description="A cold, frost-covered room. Your open cryo-pod hisses "
                    "behind you.",
        items=[scalpel],
        exits={"north": "hallway"}
    )

    hallway = Room(
        name="Hallway",
        description="A sterile, dimly lit corridor. The floor is made of "
                    "grated metal.",
        items=[],
        exits={"south": "cryo_chamber", "north": "observation_deck"}
    )

    observation_deck = Room(
        name="Observation Deck",
        description="A wide room with a reinforced glass wall overlooking "
                    "the stars.",
        items=[],
        exits={"south": "hallway"}
    )

    # World Graph mapping IDs to Room objects
    rooms = {
        "cryo_chamber": cryo_chamber,
        "hallway": hallway,
        "observation_deck": observation_deck
    }

    # Initialize Player at the Start Room
    player = Player(current_room_id="cryo_chamber")

    return WorldState(rooms=rooms, player=player)
