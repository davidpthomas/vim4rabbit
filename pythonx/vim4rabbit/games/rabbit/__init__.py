"""
Snake vs Rabbit! - Rabbit navigates a board with an enemy snake.

Rabbit head 🐰, tail ⚪, pellets 🥕🥬🥦.
Enemy snake head 🐍, tail 🟢, fixed length 13.
Snake eats pellets → ☠️ (permanent). Rabbit eats ☠️ → game over.
Rabbit hits any part of snake → game over.
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

INITIAL_PELLETS = 20
PELLETS_ON_EAT = 2
GROW_ON_EAT = 2

ENEMY_LENGTH = 13
ENEMY_TURN_CHANCE = 0.2  # 20% chance to turn each tick

# Cell rendering (each cell = 2 terminal columns)
CELL_EMPTY = "  "
CELL_HEAD = "\U0001f430"   # 🐰
CELL_TAIL = "\u26aa"       # ⚪ white circle (fluffy cotton tail)
CELL_ENEMY_HEAD = "\U0001f40d"  # 🐍 serpent
CELL_ENEMY_TAIL = "\U0001f7e2"  # 🟢 green circle
CELL_SKULL = "\u2620\ufe0f"     # ☠️ skull and crossbones
PELLET_EMOJIS = [
    "\U0001f955",  # 🥕 carrot
    "\U0001f96c",  # 🥬 lettuce
    "\U0001f966",  # 🥦 broccoli
]


class Snake:
    """Snake vs Rabbit! game."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize rabbit, enemy snake, pellets, and board dimensions."""
        # Store original terminal dimensions for restart
        self._init_width = width
        self._init_height = height
        self._reset()

    def _reset(self) -> None:
        """Reset all game state for a new round."""
        # Reserve 2 lines at bottom for status
        # Each cell is 2 terminal columns wide (for emoji support)
        self.width = max(self._init_width // 2, 10)
        self.height = max(self._init_height - 2, 10)
        self.direction = "l"  # moving right
        self.score = 0
        self._game_over = False
        self._game_over_reason = ""
        self._grow_pending = 0

        # Start snake in center, length 3, moving right
        cx = self.width // 2
        cy = self.height // 2
        self.snake: List[Tuple[int, int]] = [
            (cx, cy),       # head
            (cx - 1, cy),   # body
            (cx - 2, cy),   # tail
        ]

        # Skulls — permanent positions on the board
        self.skulls: set[Tuple[int, int]] = set()

        # Enemy snake — spawns in bottom-right quadrant, moving left
        self._init_enemy()

        # Place initial pellets — dict maps position to emoji
        self.pellets: dict[Tuple[int, int], str] = {}
        self._spawn_pellets(INITIAL_PELLETS)

    def _init_enemy(self) -> None:
        """Initialize enemy snake in bottom-right area, moving left."""
        # Place enemy in bottom-right quadrant to avoid the rabbit
        ex = self.width * 3 // 4
        ey = self.height * 3 // 4
        self.enemy_direction = "h"  # moving left
        self.enemy: List[Tuple[int, int]] = [
            ((ex + i) % self.width, ey) for i in range(ENEMY_LENGTH)
        ]

    def _spawn_pellets(self, count: int) -> None:
        """Spawn pellets in random positions not occupied by snake."""
        occupied = set(self.snake) | set(self.pellets)
        if hasattr(self, "enemy"):
            occupied |= set(self.enemy)
        if hasattr(self, "skulls"):
            occupied |= self.skulls
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

    def _tick_enemy(self) -> None:
        """Move enemy snake one step with occasional random turns."""
        # Occasionally change direction (random turn)
        if random.random() < ENEMY_TURN_CHANCE:
            if self.enemy_direction in ("h", "l"):
                perpendicular = ["j", "k"]
            else:
                perpendicular = ["h", "l"]
            self.enemy_direction = random.choice(perpendicular)

        dx, dy = DIRECTIONS[self.enemy_direction]
        head_x, head_y = self.enemy[0]

        new_x = (head_x + dx) % self.width
        new_y = (head_y + dy) % self.height

        new_head = (new_x, new_y)

        # Move: insert new head, remove tail (fixed length)
        # Snake is allowed to cross its own tail
        self.enemy.insert(0, new_head)
        self.enemy.pop()

        # Enemy hits rabbit → game over
        if new_head in self.snake:
            self._game_over = True
            self._game_over_reason = "The snake caught the rabbit!"
            return

        # Enemy eats pellet → replace with skull
        if new_head in self.pellets:
            del self.pellets[new_head]
            self.skulls.add(new_head)

    def tick(self) -> None:
        """Move rabbit and enemy one step."""
        if self._game_over:
            return

        # Move enemy first
        self._tick_enemy()
        if self._game_over:
            return

        # Move rabbit
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
            self._game_over_reason = "Rabbit hit itself!"
            return

        # Check collision with enemy snake
        if new_head in self.enemy:
            self._game_over = True
            self._game_over_reason = "Rabbit hit the snake!"
            return

        # Check skull collision
        if new_head in self.skulls:
            self._game_over = True
            self._game_over_reason = "Rabbit ate a poisoned pellet!"
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
        """Handle direction input (h/j/k/l or w/a/s/d), or play again."""
        if self._game_over and key == "p":
            self._reset()
            return
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

        # Draw skulls (permanent)
        for sx, sy in self.skulls:
            if 0 <= sx < self.width and 0 <= sy < self.height:
                grid[sy][sx] = CELL_SKULL

        # Draw enemy tail
        for x, y in self.enemy[1:]:
            if 0 <= x < self.width and 0 <= y < self.height:
                grid[y][x] = CELL_ENEMY_TAIL

        # Draw enemy head
        ex, ey = self.enemy[0]
        if 0 <= ex < self.width and 0 <= ey < self.height:
            grid[ey][ex] = CELL_ENEMY_HEAD

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
            f"  Snake vs Rabbit!  |  Score: {self.score}  |"
            "  h/j/k/l or w/a/s/d to move  |  [c] cancel"
        )
        return lines

    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Show game over screen centered in the buffer."""
        # Build the box lines (each cell = 2 terminal columns)
        inner_width = 35
        box: List[str] = []
        box.append("╔" + "═" * inner_width + "╗")
        box.append("║" + "GAME OVER!".center(inner_width) + "║")
        box.append("║" + f"Score: {self.score}".center(inner_width) + "║")
        if self._game_over_reason:
            box.append("║" + self._game_over_reason.center(inner_width) + "║")
        box.append("╚" + "═" * inner_width + "╝")

        status = "Snake vs Rabbit!  |  [p] play again?  |  [c] cancel"

        # Horizontal centering: buffer width in terminal columns = self.width * 2
        buf_cols = self.width * 2
        # Box border chars (╔║╗) are typically 1 column each in terminal
        box_width = inner_width + 2

        pad_left = max((buf_cols - box_width) // 2, 0)
        pad_str = " " * pad_left

        centered_box = [pad_str + line for line in box]

        status_pad = max((buf_cols - len(status)) // 2, 0)
        centered_status = " " * status_pad + status

        # Vertical centering: total box lines + 1 blank + 1 status
        box_height = len(centered_box) + 2  # box + blank + status
        top_pad = max((self.height - box_height) // 2, 0)

        lines: List[str] = []
        for _ in range(top_pad):
            lines.append("")
        lines.extend(centered_box)
        lines.append("")
        lines.append(centered_status)
        return lines
