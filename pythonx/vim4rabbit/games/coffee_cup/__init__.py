"""
Espresso game - ASCII cup draining animation.

Static cup outline that starts full and drains one row from top per tick.
When empty, refills and shows steam before draining again.
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
    """ASCII cup that drains."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, 30)
        self.height = max(height, 15)
        self.interior_rows = 8
        self.fill_level = self.interior_rows  # starts full
        self.steam_ticks = 0  # ticks showing steam before draining
        self.steam_max = 6
        self._game_over = False
        self._fresh = True  # show steam on first cycle

    def tick(self) -> None:
        """Drain one row or show steam."""
        # Show steam while cup is full
        if self.steam_ticks > 0:
            self.steam_ticks += 1
            if self.steam_ticks > self.steam_max:
                self.steam_ticks = 0
            return

        if self.fill_level > 0:
            self.fill_level -= 1
        else:
            # Cup is empty - refill and start steam
            self.fill_level = self.interior_rows
            self.steam_ticks = 1

    def handle_input(self, key: str) -> None:
        """No-op: espresso is non-interactive."""
        pass

    def _make_fill_row(self) -> str:
        """Generate a random fill row."""
        return "".join(random.choice(FILL_CHARS) for _ in range(CUP_WIDTH))

    def _pad(self, text: str) -> str:
        """Center text within buffer width."""
        pad = max((self.width - len(text)) // 2, 0)
        return " " * pad + text

    def get_frame(self) -> List[str]:
        """Render the coffee cup centered in the buffer."""
        lines: List[str] = []

        rim = ".---" + "-" * CUP_WIDTH + "---."
        base = "'---" + "-" * CUP_WIDTH + "---'"
        bottom = "\\" + "_" * (CUP_WIDTH - 2) + "/"

        # Steam (while cup is full)
        if self.steam_ticks > 0:
            steam_patterns = [
                "~~  ~~  ~~",
                " ~~  ~~  ~~",
                "~~  ~~  ~~",
            ]
            tick_offset = self.steam_ticks % 2
            for i, s in enumerate(steam_patterns):
                if (i + tick_offset) % 2 == 0:
                    lines.append(self._pad(s))
                else:
                    lines.append(self._pad(s.replace("~~", " ~")))
            lines.append("")
            lines.append(self._pad("*sip*"))
            lines.append("")
        else:
            # Blank lines above cup for spacing
            for _ in range(6):
                lines.append("")

        # Cup rim
        lines.append(self._pad(rim))

        # Cup body - rows from top to bottom
        # fill_level rows are filled from the bottom
        for row_idx in range(self.interior_rows):
            empty_rows = self.interior_rows - self.fill_level
            if row_idx < empty_rows:
                interior = " " * CUP_WIDTH
            else:
                interior = self._make_fill_row()
            lines.append(self._pad("|" + interior + "|"))

        # Cup base
        lines.append(self._pad(base))
        lines.append(self._pad(bottom))

        lines.append("")
        lines.append("  Coffee from Uganda  |  [c] cancel")
        return lines

    def is_game_over(self) -> bool:
        """Espresso never ends."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Not used for espresso."""
        return self.get_frame()
