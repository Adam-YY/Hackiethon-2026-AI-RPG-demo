# Iron Skeleton: Visual Novel Engine (Pygame Edition)

Iron Skeleton is a deterministic, data-driven **Visual Novel and Decision Tree engine** built in Python 3.10+. It features a beautiful, modular UI powered by `pygame_gui` and is designed for Phase 2 integration with Large Language Models (LLMs).

## Project Structure

The codebase is organized into modular components, separating data, narrative logic, and the graphical interface.

```text
HackMelb/
├── assets/themes/      # Story definitions and UI theme.json
├── logs/               # Human-readable session logs (.txt)
├── saves/              # Machine-readable state snapshots (.json)
├── game_master.py      # The "Director" - manages Dual-Mode (Logic/AI) transitions
├── interface.py        # Graphical UI Layer (pygame_gui implementation)
├── loader.py           # JSON validation and narrative/graph mapping
├── main.py             # Entry point
├── models.py           # Data structures (Scenes, Options, Player, WorldState)
├── systems.py          # Event triggers, Logging, and Memory management
├── world.py            # World state initialization helper
└── AI_model.py         # Phase 2: LLM Integration Bridge (Groq/Llama 3.1)
```

### Component Roles
- **`interface.py`**: The `VisualNovelUI` class manages the HUD, Story Log, and Dialogue boxes. It uses `pygame_gui` for a modern look and feel, including typewriter effects and floating notifications.
- **`game_master.py`**: Coordinates between the deterministic world logic and the AI takeover mode. It applies stat changes and triggers events.
- **`loader.py`**: Handles cross-file lookup between `world.json` (logic) and `story.json` (narrative).
- **`systems.py`**: Manages the persistence layer (`NarrativeLogger`, `MemoryManager`) and the `EventManager`.

## Key Features (Advanced Logic Layer)

- **Dynamic Narrative Chunking**: Narrative text is automatically split into manageable 3-sentence chunks. Players can click through chunks with a smooth, flicker-free typewriter effect (0.05s/char).
- **HP-Based Game Over**: Real-time tracking of player vitals (HP, Mana, Bullets, Credits). If HP reaches 0, the engine triggers a "SYSTEM FAILURE" state.
- **Session Persistence & Restart**: At the end of a session (narrative conclusion or death), players can choose to **RETRY SESSION** (resetting all stats and progress) or **QUIT TO DESKTOP**.
- **Mode B (AI Takeover)**: Integrated LLM support for custom player actions. When a player types a custom action, the engine enters a 3-round AI detour before re-railing back to the deterministic story graph.
- **Event-Driven Triggers**: Hidden triggers in `events.json` can modify player stats based on scene entry or specific conditions.

## UI & Aesthetics

The engine uses a **Dark Wasteland / Cyberpunk** theme defined in `assets/themes/theme.json`.
- **HUD Bar**: Displays real-time HP, Mana, Bullets, and Credits.
- **Story Log**: A vertically scrollable panel on the right tracking player choices in real-time.
- **Dialogue Box**: Features an improved typewriter effect (`TEXT_EFFECT_TYPING_APPEAR`) with manual skip support (click to show full chunk).
- **Floating Notifications**: Visual feedback for stat changes (e.g., "+20 Mana") that float up and fade away.
- **Background Music (BGM)**: Integrated `pygame.mixer` for looping background music support. The WasteLand theme includes `bgm1.mp3` for immersive atmosphere.
- **Font Optimization**: Pre-loaded font sets (`arial_bold_aa_18`, `arial_italic_aa_22`) to ensure smooth HTML tag rendering without console warnings.
- **End-Game Overlay**: Dedicated Retry/Quit buttons presented via a central UI overlay.

## Theme Creation Guide

Define your story in `assets/themes/[ThemeName]/`:
1.  **`story.json`**: Narrative scripts.
2.  **`world.json`**: Logic graph and initial player stats.
3.  **`events.json`**: Stat triggers and descriptions.

## State Management & Persistence

1.  **Narrative Log (`logs/session_*.txt`)**: Human-readable audit of the journey.
2.  **Memory Snapshot (`saves/memory.json`)**: JSON snapshot optimized for LLM context.

## Setup & Running

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start the Engine**:
    ```bash
    python3 main.py
    ```

## Phase 2: Neuro-Symbolic Integration
The engine supports a "Custom Action" button. When clicked, it enters **Mode B (AI Takeover)**, where a Llama 3.1 model generates dynamic outcomes based on player input, before re-railing back to the deterministic story graph.
