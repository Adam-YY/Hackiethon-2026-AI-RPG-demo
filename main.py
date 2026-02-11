from world import load_tutorial_world
from engine import GameEngine


def main():
    """Entry point for the Iron Skeleton text-based RPG.

    Initializes the game state and engine, then enters the REPL loop.
    """
    # Initialize the game
    state = load_tutorial_world()
    engine = GameEngine(state)

    print("--- IRON SKELETON: PHASE 1 ---")
    print("Type 'look' to see your surroundings, or 'quit' to exit.\n")
    
    # Display the starting room description
    print(engine.process_command("look"))

    while True:
        try:
            user_input = input("> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Shutting down core...")
                break

            response = engine.process_command(user_input)
            print(f"\n{response}\n")

        except (EOFError, KeyboardInterrupt):
            print("\nShutting down core...")
            break


if __name__ == "__main__":
    main()
