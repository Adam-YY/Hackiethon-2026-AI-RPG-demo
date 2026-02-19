from engine import GameEngine
import sys


def main():
    """Entry point for the Visual Novel engine loop."""
    print("--- IRON SKELETON: VISUAL NOVEL ---")
    
    theme = "WasteLand"
    if len(sys.argv) > 1:
        theme = sys.argv[1]

    try:
        engine = GameEngine(theme)
    except Exception as e:
        print(f"FAILED TO LOAD CORE: {e}")
        return

    print(f"Theme '{theme}' loaded successfully.\n")

    while True:
        # 1. Print HUD
        print(f"\n{engine.get_hud()}")
        
        # 2. Print Current Scene
        scene = engine.get_current_scene()
        print(f"\n{scene.text}")

        # 3. Handle Events
        event_descriptions = engine.handle_events()
        for desc in event_descriptions:
            print(f"\n[EVENT]: {desc}")

        # 4. Check Game Over or End State
        death_msg = engine.check_game_over()
        if death_msg:
            print(f"\n{death_msg}")
            break
            
        if scene.is_end:
            print("\n--- THE END ---")
            break

        # 5. Print Numbered Options
        print("\nChoices:")
        for opt in scene.options:
            print(f"{opt.id}. {opt.text}")

        # 6. Prompt for Input
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Shutting down core...")
                break
            
            choice_id = int(user_input)
            
            # 7. Update State and Persistence
            if not engine.select_option(choice_id):
                print(f"\nInvalid choice: {choice_id}. Please try again.")
                continue

        except ValueError:
            print("\nPlease enter a valid choice number.")
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down core...")
            break


if __name__ == "__main__":
    main()
