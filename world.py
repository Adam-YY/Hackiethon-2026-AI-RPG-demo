from loader import ThemeLoader
from models import WorldState


def load_world_from_theme(loader: ThemeLoader) -> WorldState:
    """Loads the game world state using the ThemeLoader.

    Args:
        loader (ThemeLoader): The loader instance for the current theme.

    Returns:
        WorldState: The initialized game state.
    """
    return loader.load_world()