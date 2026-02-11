from engine import GameEngine
import sys


def main():
    """Entry point for the Iron Skeleton: Advanced Logic Layer.

    Initializes the engine with a data-driven theme and runs the REPL.
    """
    print("--- IRON SKELETON: ADVANCED ---")
    
    theme = "default"
    if len(sys.argv) > 1:
        theme = sys.argv[1]

    try:
        engine = GameEngine(theme)
    except Exception as e:
        print(f"FAILED TO LOAD CORE: {e}")
        return

    print(f"Theme '{theme}' loaded successfully.")
    print("Type 'look' to begin, or 'quit' to exit.\n")
    
    # Starting look
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