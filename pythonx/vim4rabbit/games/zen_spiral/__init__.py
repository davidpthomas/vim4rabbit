"""
Zen Spiral game - Archimedean spiral animation.

Non-interactive: plots an expanding spiral using ASCII characters.
Resets when spiral exits bounds.
"""

import math
from typing import List


# Characters used for spiral points, cycling through them
SPIRAL_CHARS = [".", "o", "*", "~", "+"]


class ZenSpiral:
    """Archimedean spiral: r = a + b * theta."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, 10)
        self.height = max(height - 2, 10)
        self.theta = 0.0
        self.a = 0.0
        self.b = 0.5
        self.step = 0.3
        self.points: list = []  # list of (x, y, char_idx)
        self._game_over = False

    def tick(self) -> None:
        """Add next point on the spiral."""
        r = self.a + self.b * self.theta
        cx = self.width // 2
        cy = self.height // 2
        # Scale x by 2 for aspect ratio (chars are ~2x tall as wide)
        x = int(cx + r * math.cos(self.theta) * 2)
        y = int(cy + r * math.sin(self.theta))

        if 0 <= x < self.width and 0 <= y < self.height:
            char_idx = len(self.points) % len(SPIRAL_CHARS)
            self.points.append((x, y, char_idx))
        else:
            # Spiral exited bounds - reset
            self.points = []
            self.theta = 0.0
            return

        self.theta += self.step

    def handle_input(self, key: str) -> None:
        """No-op: zen spiral is non-interactive."""
        pass

    def get_frame(self) -> List[str]:
        """Render current spiral state."""
        grid = [[" "] * self.width for _ in range(self.height)]

        for x, y, char_idx in self.points:
            if 0 <= x < self.width and 0 <= y < self.height:
                grid[y][x] = SPIRAL_CHARS[char_idx]

        lines = ["".join(row) for row in grid]
        lines.append("")
        lines.append("  Zen Spiral  |  [c] cancel")
        return lines

    def is_game_over(self) -> bool:
        """Zen spiral never ends."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Not used for zen spiral."""
        return self.get_frame()
