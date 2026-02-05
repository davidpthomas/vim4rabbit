"""
Coffee Cup game - ASCII coffee cup filling animation.

Static cup outline with fillable interior that fills one row
from bottom per tick. When full, shows steam and "Yummm!!!" then resets.
"""

import random
from typing import List


FILL_CHARS = ["~", "=", "#", "@"]

# Cup template - the interior rows are between the rim and base
# Interior is marked with spaces between the cup walls
CUP_LEFT = "    |"
CUP_RIGHT = "|"
CUP_WIDTH = 20  # interior width


class CoffeeCup:
    """ASCII coffee cup that fills up."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, 30)
        self.height = max(height, 15)
        self.interior_rows = 8
        self.fill_level = 0  # rows filled from bottom
        self.steam_ticks = 0  # ticks showing steam after full
        self.steam_max = 6
        self._game_over = False

    def tick(self) -> None:
        """Fill one more row or show steam."""
        if self.steam_ticks > 0:
            self.steam_ticks += 1
            if self.steam_ticks > self.steam_max:
                # Reset
                self.fill_level = 0
                self.steam_ticks = 0
            return

        if self.fill_level < self.interior_rows:
            self.fill_level += 1
        else:
            # Cup is full, start steam
            self.steam_ticks = 1

    def handle_input(self, key: str) -> None:
        """No-op: coffee cup is non-interactive."""
        pass

    def _make_fill_row(self) -> str:
        """Generate a random fill row."""
        return "".join(random.choice(FILL_CHARS) for _ in range(CUP_WIDTH))

    def get_frame(self) -> List[str]:
        """Render the coffee cup."""
        lines: List[str] = []

        # Steam (only when full)
        if self.steam_ticks > 0:
            steam_patterns = [
                "       ~~  ~~  ~~",
                "      ~~  ~~  ~~",
                "       ~~  ~~  ~~",
            ]
            tick_offset = self.steam_ticks % 2
            for i, s in enumerate(steam_patterns):
                if (i + tick_offset) % 2 == 0:
                    lines.append(s)
                else:
                    lines.append(s.replace("~~", " ~"))
            lines.append("")
            lines.append("        Yummm!!!")
            lines.append("")
        else:
            # Blank lines above cup for spacing
            lines.append("")
            lines.append("")
            lines.append("")
            lines.append("")
            lines.append("")
            lines.append("")

        # Cup rim
        lines.append("    .---" + "-" * CUP_WIDTH + "---.")

        # Cup body - rows from top to bottom
        for row_idx in range(self.interior_rows):
            # row_idx 0 = top, interior_rows-1 = bottom
            # fill_level rows from bottom are filled
            fill_start = self.interior_rows - self.fill_level
            if row_idx >= fill_start:
                interior = self._make_fill_row()
            else:
                interior = " " * CUP_WIDTH
            lines.append(CUP_LEFT + interior + CUP_RIGHT)

        # Cup base
        lines.append("    '---" + "-" * CUP_WIDTH + "---'")
        lines.append("       \\" + "_" * (CUP_WIDTH - 2) + "/")

        lines.append("")
        lines.append("  Coffee Cup  |  [c] back to loading")
        return lines

    def is_game_over(self) -> bool:
        """Coffee cup never ends."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Not used for coffee cup."""
        return self.get_frame()
