"""
Game manager for mini-games during loading animation.

Module-level state + functions for managing game lifecycle.
Games are played while waiting for CodeRabbit review to complete.
"""

from typing import List, Optional

from .zen_spiral import ZenSpiral
from .coffee_cup import CoffeeCup
from .snake import Snake
from .pong import Pong
from .wargames import WarGames

# Module-level state
_active_game = None  # type: Optional[object]

# Game key -> (class, tick_ms)
GAME_REGISTRY = {
    "b": ("Coffee Break!", CoffeeCup, 1040),
    "z": ("Zen Spiral", ZenSpiral, 500),
    "s": ("Snake", Snake, 200),
    "p": ("Pong", Pong, 100),
    "w": ("Global Thermonuclear War", WarGames, 200),
}


def get_game_menu() -> List[str]:
    """Render game selection menu."""
    return [
        "",
        "",
        "   ╔════════════════════════════════════════════╗",
        "   ║           🎮  Mini-Games  🎮               ║",
        "   ╠════════════════════════════════════════════╣",
        "   ║                                            ║",
        "   ║   [b]  Coffee Break!                       ║",
        "   ║   [z]  Zen Spiral                          ║",
        "   ║   [s]  Snake                               ║",
        "   ║   [p]  Pong                                ║",
        "   ║   [w]  Global Thermonuclear War            ║",
        "   ║                                            ║",
        "   ║   Press key to start game                  ║",
        "   ║   [c] to go back                           ║",
        "   ║                                            ║",
        "   ╚════════════════════════════════════════════╝",
        "",
    ]


def start_game(key: str, width: int, height: int) -> bool:
    """Create and activate a game. Returns True if game started."""
    global _active_game
    if key not in GAME_REGISTRY:
        return False
    _, game_class, _ = GAME_REGISTRY[key]
    _active_game = game_class(width, height)
    return True


def stop_game() -> None:
    """Clear active game."""
    global _active_game
    _active_game = None


def is_game_active() -> bool:
    """Check if a game is currently active."""
    return _active_game is not None


def get_tick_rate(key: str) -> int:
    """Get tick rate in ms for a game key."""
    if key in GAME_REGISTRY:
        return GAME_REGISTRY[key][2]
    return 500


def tick_game() -> List[str]:
    """Advance game one step and return rendered frame."""
    if _active_game is None:
        return []
    _active_game.tick()
    if _active_game.is_game_over():
        return _active_game.get_game_over_frame()
    return _active_game.get_frame()


def input_game(key: str) -> List[str]:
    """Handle input and return rendered frame."""
    if _active_game is None:
        return []
    _active_game.handle_input(key)
    if _active_game.is_game_over():
        return _active_game.get_game_over_frame()
    return _active_game.get_frame()
