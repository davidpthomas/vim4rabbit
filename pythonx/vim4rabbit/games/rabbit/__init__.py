"""
Rabbit game - Classic snake with h/j/k/l and w/a/s/d controls.

Rabbit head 🐰, tail ⚪, pellets 🥕🥬🥦.
Each grid cell is 2 terminal columns wide to support emoji rendering.
Wraps around edges, game over on self-collision.
"""

import random
from typing import List, Tuple


# Directions: (dx, dy)
DIRECTIONS = {
    "h": (-1, 0),   # left
    "l": (1, 0),    # right
    "k": (0, -1),   # up
    "j": (0, 1),    # down
}

# WASD aliases → canonical vim keys
WASD_MAP = {
    "a": "h",
    "d": "l",
    "w": "k",
    "s": "j",
}

# Opposite directions (can't reverse into yourself)
OPPOSITES = {
    "h": "l",
    "l": "h",
    "k": "j",
    "j": "k",
}

INITIAL_PELLETS = 5
PELLETS_ON_EAT = 2
GROW_ON_EAT = 2

# Cell rendering (each cell = 2 terminal columns)
CELL_EMPTY = "  "
CELL_HEAD = "\U0001f430"   # 🐰
CELL_TAIL = "\u26aa"       # ⚪ white circle (fluffy cotton tail)
PELLET_EMOJIS = [
    "\U0001f955",  # 🥕 carrot
    "\U0001f96c",  # 🥬 lettuce
    "\U0001f966",  # 🥦 broccoli
]


class Snake:
    """Classic rabbit (snake) game."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize rabbit, pellets, and board dimensions."""
        # Reserve 2 lines at bottom for status
        # Each cell is 2 terminal columns wide (for emoji support)
        self.width = max(width // 2, 10)
        self.height = max(height - 2, 10)
        self.direction = "l"  # moving right
        self.score = 0
        self._game_over = False
        self._grow_pending = 0

        # Start snake in center, length 3, moving right
        cx = self.width // 2
        cy = self.height // 2
        self.snake: List[Tuple[int, int]] = [
            (cx, cy),       # head
            (cx - 1, cy),   # body
            (cx - 2, cy),   # tail
        ]

        # Place initial pellets — dict maps position to emoji
        self.pellets: dict[Tuple[int, int], str] = {}
        self._spawn_pellets(INITIAL_PELLETS)

    def _spawn_pellets(self, count: int) -> None:
        """Spawn pellets in random positions not occupied by snake."""
        occupied = set(self.snake) | set(self.pellets)
        available = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in occupied
        ]
        if not available:
            return
        count = min(count, len(available))
        new_positions = random.sample(available, count)
        for pos in new_positions:
            self.pellets[pos] = random.choice(PELLET_EMOJIS)

    def tick(self) -> None:
        """Move snake one step."""
        if self._game_over:
            return

        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.snake[0]

        # Wrap around edges
        new_x = (head_x + dx) % self.width
        new_y = (head_y + dy) % self.height

        new_head = (new_x, new_y)

        # Check self-collision (against body, not including tail that's about to move)
        # The tail will move unless we're growing, so check accordingly
        check_body = self.snake[:-1] if self._grow_pending == 0 else self.snake
        if new_head in check_body:
            self._game_over = True
            return

        # Move: insert new head
        self.snake.insert(0, new_head)

        # Check pellet
        if new_head in self.pellets:
            del self.pellets[new_head]
            self.score += 1
            self._grow_pending += GROW_ON_EAT
            self._spawn_pellets(PELLETS_ON_EAT)

        # Remove tail unless growing
        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self.snake.pop()

    def handle_input(self, key: str) -> None:
        """Handle direction input (h/j/k/l or w/a/s/d)."""
        key = WASD_MAP.get(key, key)
        if key in DIRECTIONS and key != OPPOSITES.get(self.direction):
            self.direction = key

    def get_frame(self) -> List[str]:
        """Render current game state. Each cell is 2 terminal columns."""
        grid = [[CELL_EMPTY] * self.width for _ in range(self.height)]

        # Draw pellets (each with its own random emoji)
        for (px, py), emoji in self.pellets.items():
            if 0 <= px < self.width and 0 <= py < self.height:
                grid[py][px] = emoji

        # Draw rabbit tail (all body segments)
        for x, y in self.snake[1:]:
            if 0 <= x < self.width and 0 <= y < self.height:
                grid[y][x] = CELL_TAIL

        # Draw rabbit head
        hx, hy = self.snake[0]
        if 0 <= hx < self.width and 0 <= hy < self.height:
            grid[hy][hx] = CELL_HEAD

        lines = ["".join(row) for row in grid]
        lines.append("")
        lines.append(
            f"  Rabbit  |  Score: {self.score}  |  h/j/k/l or w/a/s/d to move  |  [c] cancel"
        )
        return lines

    def is_game_over(self) -> bool:
        """Check if snake hit itself."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Show game over screen."""
        lines: List[str] = []
        lines.append("")
        lines.append("")
        lines.append("")
        cy = self.height // 2 - 3
        for _ in range(max(cy, 0)):
            lines.append("")
        lines.append("        ╔═══════════════════════╗")
        lines.append("        ║      GAME OVER!       ║")
        lines.append(f"        ║     Score: {self.score:<10} ║")
        lines.append("        ╚═══════════════════════╝")
        lines.append("")
        lines.append("  Rabbit  |  [c] cancel")
        return lines
