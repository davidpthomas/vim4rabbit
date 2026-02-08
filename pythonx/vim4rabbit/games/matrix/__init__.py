"""
Matrix game - falling digital rain animation.

Non-interactive: columns of ASCII characters cascade down independently.
Occasional rabbit-themed easter eggs appear in the streams.

Color zones within each column trail (position-based, mapped via Vim
highlight matching on character classes that change per character set):
  trail  -> Dark Green (#003B00)  trailing chars
  body   -> Islam Green (#008F11) body of streak
  head   -> Erin (#00FF41)        leading edge
  white  -> White (#FFFFFF)       rare head flash

Character sets (user selects with 'n', 's', 'r'):
  number   -> digits 0-9 (default)
  symbol   -> emoji symbols
  rabbit   -> rabbit-themed emoji

Each grid cell is 2 terminal columns wide so that emoji (which occupy
2 cells) and space-padded ASCII characters share the same layout.
"""

import random
from typing import List


# Character sets — each subdivided into 4 zone pools for highlight matching.
# Pools are lists of 2-cell-wide strings. Within each set, zone pools must
# use disjoint entries.
CHAR_SETS = [
    {
        "name": "Numbers",
        "trail": ["0 ", "1 ", "2 "],
        "body": ["3 ", "4 ", "5 "],
        "head": ["6 ", "7 ", "8 "],
        "white": ["9 "],
    },
    {
        "name": "Symbol",
        "trail": ["\U0001f539", "\U0001f538", "\U0001f4a0", "\U0001f53b", "\U0001f53a"],
        "body": ["\U0001f48e", "\U0001f52e", "\U0001f3b2", "\U0001f511", "\U0001f4a3"],
        "head": ["\U0001f525", "\U0001f4ab", "\U0001f300", "\U0001f30a"],
        "white": ["\U0001f4a5", "\U0001f4a2"],
    },
    {
        "name": "Rabbit",
        "trail": ["\U0001f331", "\U0001f343", "\U0001f33f", "\U0001f340", "\U0001f96c"],
        "body": ["\U0001f407", "\U0001f955", "\U0001f95a", "\U0001f41b", "\U0001f966"],
        "head": ["\U0001f430", "\U0001f43e", "\U0001f33e", "\U0001f41d"],
        "white": ["\U0001f31f", "\u2728"],
    },
]

DEFAULT_CHAR_SET = 0  # number

# Key -> char set index for direct selection
CHAR_SET_KEYS = {"n": 0, "s": 1, "r": 2}

# Probability that the very head character flashes white
WHITE_CHANCE = 0.05

# Rabbit-themed words that occasionally appear in streams
RABBIT_WORDS = ["RABBIT", "CARROT", "BURROW", "WARREN", "HOPPER"]

# Mapping from ASCII letter to emoji for rabbit-word rendering when the
# Rabbit character set is active.
RABBIT_LETTER_EMOJI = {
    "R": "\U0001f430",  # 🐰
    "A": "\U0001f955",  # 🥕
    "B": "\U0001f407",  # 🐇
    "I": "\U0001f331",  # 🌱
    "T": "\U0001f33f",  # 🌿
    "C": "\U0001f340",  # 🍀
    "O": "\U0001f95a",  # 🥚
    "U": "\U0001f43e",  # 🐾
    "W": "\U0001f33e",  # 🌾
    "E": "\U0001f41b",  # 🐛
    "N": "\U0001f41d",  # 🐝
    "H": "\U0001f343",  # 🍃
    "P": "\U0001f31f",  # 🌟
}

# Probability (per column per reset) of injecting a rabbit word
RABBIT_CHANCE = 0.08

# Rabbit emoji that blink (eating animation) — visible 3 frames, hidden 1
BLINK_CELLS = {"\U0001f430", "\U0001f407"}  # 🐰, 🐇
BLINK_PERIOD = 4  # total cycle length in ticks
BLINK_OFF = 1     # number of ticks hidden per cycle

MIN_WIDTH = 20
MIN_HEIGHT = 10
RESERVED_LINES = 2  # bottom lines for status prompt

# Seed range for character shape indices
_SEED_MAX = 255


def _zone_cell(seed: int, pool: list) -> str:
    """Map an integer seed to a 2-cell string in the given pool."""
    return pool[seed % len(pool)]


class _Column:
    """State for a single falling column."""

    __slots__ = ("speed", "delay", "head", "trail_len", "chars", "height",
                 "rabbit_word", "rabbit_offset")

    def __init__(self, height: int) -> None:
        self.height = height
        self.speed = random.randint(1, 3)
        self.delay = random.randint(0, height)
        self.head = -self.delay
        self.trail_len = random.randint(8, max(10, height))
        self.chars = [random.randint(0, _SEED_MAX) for _ in range(self.trail_len)]
        self.rabbit_word: str = ""
        self.rabbit_offset = 0
        self._maybe_assign_rabbit()

    def _maybe_assign_rabbit(self) -> None:
        if random.random() < RABBIT_CHANCE:
            self.rabbit_word = random.choice(RABBIT_WORDS)
            self.rabbit_offset = random.randint(0, max(0, self.trail_len - len(self.rabbit_word)))

    def reset(self) -> None:
        self.speed = random.randint(1, 3)
        self.delay = random.randint(0, self.height // 2)
        self.head = -self.delay
        self.trail_len = random.randint(8, max(10, self.height))
        self.chars = [random.randint(0, _SEED_MAX) for _ in range(self.trail_len)]
        self.rabbit_word = ""
        self.rabbit_offset = 0
        self._maybe_assign_rabbit()


class Matrix:
    """Falling digital rain a la The Matrix, with rabbit-hole easter eggs."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, MIN_WIDTH)
        self.height = max(height - RESERVED_LINES, MIN_HEIGHT)
        self._game_over = False
        self._tick_count = 0
        self._char_set_idx = DEFAULT_CHAR_SET
        self.num_columns = self.width // 2
        self._columns = [_Column(self.height) for _ in range(self.num_columns)]

    def tick(self) -> None:
        """Advance each column according to its own speed."""
        self._tick_count += 1
        for col in self._columns:
            if self._tick_count % col.speed != 0:
                continue
            col.head += 1
            # Scramble one random seed in the trail each advance
            if col.chars:
                idx = random.randint(0, len(col.chars) - 1)
                col.chars[idx] = random.randint(0, _SEED_MAX)
            # Reset column when entire trail has scrolled off screen
            if col.head - col.trail_len >= self.height:
                col.reset()

    def handle_input(self, key: str) -> None:
        """Handle user input. 'n'/'s'/'r' select character set."""
        if key in CHAR_SET_KEYS:
            self._char_set_idx = CHAR_SET_KEYS[key]

    def _trail_cell(self, col: _Column, i: int) -> str:
        """Resolve a trail position to a 2-cell string in the correct color zone.

        Position i=0 is the head (leading edge), i=trail_len-1 is the tail.
        The trail is split into equal thirds:
          head third  -> head pool  (Erin bright green)
          body third  -> body pool  (Islam green)
          tail third  -> trail pool (Dark green)
        The very head (i==0) has a small chance of flashing white.
        """
        seed = col.chars[i % len(col.chars)]
        cs = CHAR_SETS[self._char_set_idx]
        third = max(col.trail_len // 3, 1)

        if i == 0 and random.random() < WHITE_CHANCE:
            return _zone_cell(seed, cs["white"])
        if i < third:
            return _zone_cell(seed, cs["head"])
        if i < 2 * third:
            return _zone_cell(seed, cs["body"])
        return _zone_cell(seed, cs["trail"])

    def _rabbit_letter_cell(self, letter: str) -> str:
        """Convert a single ASCII letter to a 2-cell string.

        When the Rabbit character set is active, letters are mapped to emoji
        via RABBIT_LETTER_EMOJI.  Otherwise they are space-padded ASCII.
        """
        cs = CHAR_SETS[self._char_set_idx]
        if cs["name"] == "Rabbit":
            return RABBIT_LETTER_EMOJI.get(letter, letter + " ")
        return letter + " "

    def get_frame(self) -> List[str]:
        """Render current matrix state as list of strings."""
        grid = [["  "] * self.num_columns for _ in range(self.height)]

        for x, col in enumerate(self._columns):
            for i in range(col.trail_len):
                row = col.head - i
                if 0 <= row < self.height:
                    # Check if this position falls within a rabbit word
                    if (col.rabbit_word
                            and col.rabbit_offset <= i < col.rabbit_offset + len(col.rabbit_word)):
                        char_pos = i - col.rabbit_offset
                        grid[row][x] = self._rabbit_letter_cell(col.rabbit_word[char_pos])
                    else:
                        grid[row][x] = self._trail_cell(col, i)

        # Blink rabbit emoji: hide for BLINK_OFF ticks out of every BLINK_PERIOD
        if self._tick_count % BLINK_PERIOD < BLINK_OFF:
            for row in grid:
                for j, cell in enumerate(row):
                    if cell in BLINK_CELLS:
                        row[j] = "  "

        odd_pad = " " if self.width % 2 else ""
        lines = ["".join(row) + odd_pad for row in grid]

        # Status line with mode selection and cancel
        lines.append("")
        labels = []
        for key, idx in sorted(CHAR_SET_KEYS.items(), key=lambda kv: kv[1]):
            name = CHAR_SETS[idx]["name"].lower()
            entry = "[" + key + "]" + name[1:]
            if idx == self._char_set_idx:
                entry = "*" + entry
            else:
                entry = " " + entry
            labels.append(entry)
        lines.append("  ".join(labels) + "   [c]ancel")
        return lines

    def get_match_patterns(self) -> List[List[str]]:
        """Return Vim matchadd patterns for the current character set.

        Each entry is [highlight_group, vim_regex_pattern].
        For ASCII sets (space-padded single chars), uses [chars] bracket syntax.
        For emoji sets, uses \\%(e1\\|e2\\|...) alternation.
        """
        cs = CHAR_SETS[self._char_set_idx]
        # Emoji cells are single wide chars; space-padded ASCII cells are 2 chars
        is_emoji = len(cs["trail"][0]) == 1

        result = []
        for zone, group in [("trail", "MatrixTrail"), ("body", "MatrixBody"),
                            ("head", "MatrixHead"), ("white", "MatrixWhite")]:
            pool = cs[zone]
            if is_emoji:
                inner = "\\|".join(pool)
                pattern = "\\%(" + inner + "\\)"
            else:
                chars = "".join(cell[0] for cell in pool)
                pattern = "[" + chars + "]"
            result.append([group, pattern])
        return result

    def is_game_over(self) -> bool:
        """Matrix never ends on its own."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Not used for matrix."""
        return self.get_frame()
