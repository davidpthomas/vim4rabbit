"""Tests for vim4rabbit.games.matrix module."""

import unicodedata

import pytest
from vim4rabbit.games.matrix import (
    Matrix, _Column, _zone_cell, _SEED_MAX,
    CHAR_SETS, CHAR_SET_KEYS, DEFAULT_CHAR_SET, WHITE_CHANCE,
    RABBIT_WORDS, RABBIT_CHANCE, RABBIT_LETTER_EMOJI,
    BLINK_CELLS, BLINK_PERIOD, BLINK_OFF,
    MIN_WIDTH, MIN_HEIGHT, RESERVED_LINES,
)


def _display_width(s):
    """Return the terminal display width of a string.

    East-Asian wide/fullwidth characters (including most emoji) occupy
    2 terminal cells; everything else occupies 1.
    """
    w = 0
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        w += 2 if eaw in ("W", "F") else 1
    return w


def _all_pool_cells(cs_idx):
    """Collect all zone pool cells for a given char set."""
    cs = CHAR_SETS[cs_idx]
    return cs["trail"] + cs["body"] + cs["head"] + cs["white"]


class TestZoneCell:
    """Tests for _zone_cell seed-to-cell mapping."""

    def test_maps_to_pool(self):
        """Test that every seed maps to a cell within the pool."""
        pool = CHAR_SETS[0]["trail"]
        for seed in range(50):
            assert _zone_cell(seed, pool) in pool

    def test_deterministic(self):
        """Test that same seed always produces the same cell."""
        pool = CHAR_SETS[0]["head"]
        for seed in range(20):
            assert _zone_cell(seed, pool) == _zone_cell(seed, pool)

    def test_wraps_around(self):
        """Test that seed wraps around the pool length."""
        pool = CHAR_SETS[0]["trail"]
        assert _zone_cell(0, pool) == _zone_cell(len(pool), pool)


class TestCharSets:
    """Tests for CHAR_SETS configuration."""

    def test_three_char_sets(self):
        """Test that exactly three character sets are defined."""
        assert len(CHAR_SETS) == 3

    def test_each_set_has_required_keys(self):
        """Test that each character set has all required zone keys."""
        for cs in CHAR_SETS:
            assert "name" in cs
            assert "trail" in cs
            assert "body" in cs
            assert "head" in cs
            assert "white" in cs

    def test_zone_pools_are_disjoint(self):
        """Within each char set, zone pools must not share cells."""
        for cs in CHAR_SETS:
            pools = [cs["trail"], cs["body"], cs["head"], cs["white"]]
            all_cells = []
            for pool in pools:
                all_cells.extend(pool)
            assert len(all_cells) == len(set(all_cells)), (
                f"Duplicate cells in {cs['name']}: {all_cells}"
            )

    def test_default_is_numbers(self):
        """Test that default character set is Numbers."""
        assert DEFAULT_CHAR_SET == 0
        assert CHAR_SETS[0]["name"] == "Numbers"

    def test_names(self):
        """Test that all expected character set names are present."""
        names = [cs["name"] for cs in CHAR_SETS]
        assert "Numbers" in names
        assert "Symbol" in names
        assert "Rabbit" in names

    def test_pools_are_lists(self):
        """All zone pools must be lists of strings."""
        for cs in CHAR_SETS:
            for zone in ("trail", "body", "head", "white"):
                assert isinstance(cs[zone], list), (
                    f"{cs['name']}.{zone} should be a list"
                )
                for cell in cs[zone]:
                    assert isinstance(cell, str)

    def test_cells_are_2_display_width(self):
        """Every cell should occupy exactly 2 terminal columns."""
        for cs in CHAR_SETS:
            for zone in ("trail", "body", "head", "white"):
                for cell in cs[zone]:
                    assert _display_width(cell) == 2, (
                        f"{cs['name']}.{zone} cell {cell!r} is "
                        f"{_display_width(cell)} wide, expected 2"
                    )


class TestColumnInit:
    """Tests for _Column initialization."""

    def test_column_has_required_attrs(self):
        """Test that column has all required attributes."""
        col = _Column(20)
        assert hasattr(col, "speed")
        assert hasattr(col, "delay")
        assert hasattr(col, "head")
        assert hasattr(col, "trail_len")
        assert hasattr(col, "chars")

    def test_speed_range(self):
        """Test that speed is always between 1 and 3."""
        for _ in range(50):
            col = _Column(20)
            assert 1 <= col.speed <= 3

    def test_delay_range(self):
        """Test that delay is within valid range."""
        for _ in range(50):
            col = _Column(20)
            assert 0 <= col.delay <= 20

    def test_head_starts_negative(self):
        """Test that head starts at or below zero."""
        col = _Column(20)
        assert col.head <= 0

    def test_trail_len_minimum(self):
        """Test that trail length is at least 8."""
        col = _Column(20)
        assert col.trail_len >= 8

    def test_chars_length_matches_trail(self):
        """Test that chars list length matches trail length."""
        col = _Column(20)
        assert len(col.chars) == col.trail_len

    def test_chars_are_integer_seeds(self):
        """Test that chars are integer seeds within valid range."""
        col = _Column(20)
        for seed in col.chars:
            assert isinstance(seed, int)
            assert 0 <= seed <= _SEED_MAX

    def test_reset_changes_state(self):
        """Test that reset re-randomizes column parameters."""
        col = _Column(20)
        col.head = 100
        col.reset()
        assert col.head <= 0
        assert len(col.chars) == col.trail_len


class TestColumnRabbitWord:
    """Tests for rabbit word easter egg in columns."""

    def test_rabbit_word_from_list_or_empty(self):
        """Test that rabbit word is from the word list or empty."""
        col = _Column(20)
        assert col.rabbit_word in RABBIT_WORDS or col.rabbit_word == ""

    def test_rabbit_offset_valid(self):
        """Test that rabbit word offset fits within the trail."""
        col = _Column(20)
        if col.rabbit_word:
            assert col.rabbit_offset >= 0
            assert col.rabbit_offset + len(col.rabbit_word) <= col.trail_len

    def test_force_rabbit_word(self):
        """Ensure rabbit words can appear by trying many columns."""
        found = False
        for _ in range(500):
            col = _Column(30)
            if col.rabbit_word:
                found = True
                break
        assert found, "Expected at least one rabbit word in 500 columns"


class TestMatrixInit:
    """Tests for Matrix initialization."""

    def test_default_dimensions(self):
        """Test that normal dimensions are stored correctly."""
        game = Matrix(60, 30)
        assert game.width == 60
        assert game.height == 28

    def test_minimum_width(self):
        """Test that small width is clamped to minimum."""
        game = Matrix(5, 30)
        assert game.width == MIN_WIDTH

    def test_minimum_height(self):
        """Test that small height is clamped to minimum."""
        game = Matrix(60, 5)
        assert game.height == MIN_HEIGHT

    def test_column_count_matches_num_columns(self):
        """Test that column list length matches num_columns."""
        game = Matrix(40, 20)
        assert len(game._columns) == game.num_columns

    def test_num_columns_is_half_width(self):
        """Test that num_columns is width divided by 2."""
        game = Matrix(40, 20)
        assert game.num_columns == game.width // 2

    def test_initial_state(self):
        """Test that initial state has zero tick count and default char set."""
        game = Matrix(40, 20)
        assert game._tick_count == 0
        assert game._char_set_idx == DEFAULT_CHAR_SET
        assert game.is_game_over() is False


class TestMatrixTick:
    """Tests for Matrix.tick method."""

    def test_tick_increments_count(self):
        """Test that tick increments the tick counter."""
        game = Matrix(40, 20)
        game.tick()
        assert game._tick_count == 1

    def test_multiple_ticks(self):
        """Test that tick counter accumulates correctly."""
        game = Matrix(40, 20)
        for _ in range(10):
            game.tick()
        assert game._tick_count == 10

    def test_columns_advance(self):
        """Test that at least some columns advance after ticks."""
        game = Matrix(40, 20)
        initial_heads = [col.head for col in game._columns]
        for _ in range(6):
            game.tick()
        current_heads = [col.head for col in game._columns]
        advanced = sum(1 for i, c in enumerate(current_heads) if c > initial_heads[i])
        assert advanced > 0

    def test_column_resets_after_scrolling_off(self):
        """Test that columns reset after scrolling past the bottom."""
        game = Matrix(20, 15)
        for _ in range(200):
            game.tick()
        for col in game._columns:
            assert col.head - col.trail_len < game.height

    def test_seed_scrambling(self):
        """Test that character seeds change over time."""
        game = Matrix(20, 15)
        col = game._columns[0]
        col.head = 5
        col.delay = 0
        col.speed = 1
        initial_seeds = col.chars[:]
        for _ in range(50):
            game.tick()
        assert col.chars != initial_seeds or col.head != 5


class TestTrailCell:
    """Tests for Matrix._trail_cell zone mapping."""

    def _make_game_and_col(self, char_set_idx=0):
        """Create a game and configure its first column for testing."""
        game = Matrix(40, 20)
        game._char_set_idx = char_set_idx
        col = game._columns[0]
        col.trail_len = 12
        col.chars = list(range(12))
        return game, col

    def test_head_zone_returns_head_or_white(self):
        """Test that position 0 returns head or white pool cells."""
        game, col = self._make_game_and_col()
        cs = CHAR_SETS[0]
        results = set()
        for _ in range(100):
            ch = game._trail_cell(col, 0)
            results.add(ch)
        valid = cs["head"] + cs["white"]
        for ch in results:
            assert ch in valid

    def test_body_zone_returns_body_pool_cell(self):
        """Test that middle positions return body pool cells."""
        game, col = self._make_game_and_col()
        cs = CHAR_SETS[0]
        ch = game._trail_cell(col, 5)
        assert ch in cs["body"]

    def test_trail_zone_returns_trail_pool_cell(self):
        """Test that tail positions return trail pool cells."""
        game, col = self._make_game_and_col()
        cs = CHAR_SETS[0]
        ch = game._trail_cell(col, 9)
        assert ch in cs["trail"]

    def test_white_flash_can_occur(self):
        """Test that white flash appears at head position."""
        game, col = self._make_game_and_col()
        cs = CHAR_SETS[0]
        found = False
        for _ in range(500):
            ch = game._trail_cell(col, 0)
            if ch in cs["white"]:
                found = True
                break
        assert found, "Expected white flash at head in 500 tries"

    def test_non_head_never_white(self):
        """Test that non-head positions never produce white cells."""
        game, col = self._make_game_and_col()
        cs = CHAR_SETS[0]
        for _ in range(200):
            for i in range(1, col.trail_len):
                ch = game._trail_cell(col, i)
                assert ch not in cs["white"]

    def test_equal_green_distribution(self):
        """Test that head, body, and trail zones each get enough cells."""
        game, col = self._make_game_and_col()
        col.trail_len = 30
        col.chars = list(range(30))
        cs = CHAR_SETS[0]
        head_count = body_count = trail_count = 0
        for i in range(col.trail_len):
            ch = game._trail_cell(col, i)
            if ch in cs["head"] or ch in cs["white"]:
                head_count += 1
            elif ch in cs["body"]:
                body_count += 1
            elif ch in cs["trail"]:
                trail_count += 1
        assert head_count >= 8
        assert body_count >= 8
        assert trail_count >= 8

    def test_uses_current_char_set(self):
        """Switching char set changes the cells produced."""
        game, col = self._make_game_and_col(0)
        cs0 = CHAR_SETS[0]
        ch0 = game._trail_cell(col, 5)
        assert ch0 in cs0["body"]

        game._char_set_idx = 1
        cs1 = CHAR_SETS[1]
        ch1 = game._trail_cell(col, 5)
        assert ch1 in cs1["body"]


class TestCharSetSelection:
    """Tests for character set selection via handle_input."""

    def test_select_number(self):
        """Test that n key selects the Numbers char set."""
        game = Matrix(40, 20)
        game.handle_input("s")
        assert game._char_set_idx == 1
        game.handle_input("n")
        assert game._char_set_idx == 0

    def test_select_symbol(self):
        """Test that s key selects the Symbol char set."""
        game = Matrix(40, 20)
        game.handle_input("s")
        assert game._char_set_idx == 1

    def test_select_rabbit(self):
        """Test that r key selects the Rabbit char set."""
        game = Matrix(40, 20)
        game.handle_input("r")
        assert game._char_set_idx == 2

    def test_keys_match_char_set_keys(self):
        """Test that all CHAR_SET_KEYS map to correct indices."""
        game = Matrix(40, 20)
        for key, idx in CHAR_SET_KEYS.items():
            game.handle_input(key)
            assert game._char_set_idx == idx

    def test_non_mode_keys_ignored(self):
        """Test that unrecognized keys do not change char set."""
        game = Matrix(40, 20)
        game.handle_input("h")
        game.handle_input("x")
        assert game._char_set_idx == 0

    def test_frame_cells_match_active_set(self):
        """After toggling, frame cells come from the new char set."""
        game = Matrix(40, 20)
        for col in game._columns:
            col.rabbit_word = ""
            col.head = 8
            col.delay = 0
            col.speed = 1
        game.tick()

        for cs_idx in range(len(CHAR_SETS)):
            game._char_set_idx = cs_idx
            valid = _all_pool_cells(cs_idx)
            frame = game.get_frame()
            for line in frame[:game.height]:
                # Iterate in 2-cell chunks
                pos = 0
                while pos < len(line):
                    ch = line[pos]
                    if ch == " ":
                        pos += 1
                        continue
                    # Try to extract a 2-cell chunk
                    eaw = unicodedata.east_asian_width(ch)
                    if eaw in ("W", "F"):
                        cell = ch
                        pos += 1
                    else:
                        cell = line[pos:pos + 2]
                        pos += 2
                    if cell.strip():
                        assert cell in valid, (
                            f"Cell {cell!r} not in set {CHAR_SETS[cs_idx]['name']}"
                        )


class TestMatchPatterns:
    """Tests for get_match_patterns method."""

    def test_returns_four_patterns(self):
        """Test that four highlight patterns are returned."""
        game = Matrix(40, 20)
        patterns = game.get_match_patterns()
        assert len(patterns) == 4

    def test_pattern_structure(self):
        """Test that each pattern is a group name and valid regex."""
        game = Matrix(40, 20)
        for group, pattern in game.get_match_patterns():
            assert isinstance(group, str)
            is_bracket = pattern.startswith("[") and pattern.endswith("]")
            is_alternation = pattern.startswith("\\%(") and pattern.endswith("\\)")
            assert is_bracket or is_alternation

    def test_number_set_uses_bracket_pattern(self):
        """Test that Numbers set uses bracket character class patterns."""
        game = Matrix(40, 20)
        game._char_set_idx = 0  # Numbers
        for _, pattern in game.get_match_patterns():
            assert pattern.startswith("[") and pattern.endswith("]")

    def test_emoji_sets_use_alternation_pattern(self):
        """Test that emoji sets use Vim alternation patterns."""
        game = Matrix(40, 20)
        for cs_idx in (1, 2):  # Symbol and Rabbit
            game._char_set_idx = cs_idx
            for _, pattern in game.get_match_patterns():
                assert pattern.startswith("\\%(") and pattern.endswith("\\)")

    def test_highlight_groups(self):
        """Test that highlight group names are correct."""
        game = Matrix(40, 20)
        groups = [p[0] for p in game.get_match_patterns()]
        assert groups == ["MatrixTrail", "MatrixBody", "MatrixHead", "MatrixWhite"]

    def test_patterns_change_with_char_set(self):
        """Test that patterns differ between character sets."""
        game = Matrix(40, 20)
        p0 = game.get_match_patterns()
        game.handle_input("s")
        p1 = game.get_match_patterns()
        assert p0 != p1

    def test_default_patterns_use_digits(self):
        """Test that default patterns contain digit characters."""
        game = Matrix(40, 20)
        patterns = game.get_match_patterns()
        # Default is numbers — trail pattern should contain digits
        trail_pattern = patterns[0][1]
        assert "0" in trail_pattern


class TestStatusLine:
    """Tests for the status/toggle line in frames."""

    def test_status_shows_mode_keys(self):
        """Test that status line shows all char set key hints."""
        game = Matrix(40, 20)
        frame = game.get_frame()
        assert "[n]" in frame[-1]
        assert "[s]" in frame[-1]
        assert "[r]" in frame[-1]

    def test_status_shows_cancel(self):
        """Test that status line shows cancel and game name."""
        game = Matrix(40, 20)
        frame = game.get_frame()
        assert "[c] cancel" in frame[-1]
        assert "Enter the Matrix" in frame[-1]

    def test_status_marks_active_set(self):
        """Test that active character set is marked with asterisk."""
        game = Matrix(40, 20)
        frame = game.get_frame()
        # Default is number — should have * before [n]
        assert "*[n]" in frame[-1]

    def test_status_updates_after_selection(self):
        """Test that asterisk moves when char set is changed."""
        game = Matrix(40, 20)
        game.handle_input("s")
        frame = game.get_frame()
        assert "*[s]" in frame[-1]
        game.handle_input("r")
        frame = game.get_frame()
        assert "*[r]" in frame[-1]


class TestMatrixGetFrame:
    """Tests for Matrix.get_frame method."""

    def test_frame_line_count(self):
        """Test that frame has correct total number of lines."""
        game = Matrix(40, 20)
        frame = game.get_frame()
        assert len(frame) == game.height + RESERVED_LINES

    def test_frame_display_width(self):
        """Each grid line should be exactly game.width terminal columns."""
        game = Matrix(40, 20)
        frame = game.get_frame()
        for line in frame[:game.height]:
            assert _display_width(line) == game.width

    def test_frame_display_width_odd(self):
        """Odd widths get a trailing space pad."""
        game = Matrix(41, 20)
        frame = game.get_frame()
        for line in frame[:game.height]:
            assert _display_width(line) == game.width

    def test_frame_after_ticks_has_characters(self):
        """Test that frame contains non-space characters after ticking."""
        game = Matrix(40, 20)
        for col in game._columns[:5]:
            col.head = 5
            col.delay = 0
            col.speed = 1
        game.tick()
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        non_space = sum(1 for c in grid_text if c != " ")
        assert non_space > 0

    def test_empty_frame_initially_possible(self):
        """Test that frame can be empty when all columns are delayed."""
        game = Matrix(40, 20)
        for col in game._columns:
            col.head = -100
            col.delay = 100
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert grid_text.strip() == ""

    def test_rabbit_word_appears_in_frame(self):
        """Test that a rabbit word letter appears in the frame."""
        game = Matrix(40, 20)
        col = game._columns[3]
        col.rabbit_word = "RABBIT"
        col.rabbit_offset = 0
        col.trail_len = max(col.trail_len, len("RABBIT"))
        col.chars = list(range(col.trail_len))
        col.head = 5
        col.speed = 1
        col.delay = 0
        frame = game.get_frame()
        # Collect cells from column 3 (cells start at char position 6, each 2 wide)
        grid_text = "".join(frame[:game.height])
        # Should contain an "R" (space-padded) since default is Numbers set
        assert "R " in grid_text

    def test_rabbit_word_emoji_in_rabbit_set(self):
        """Rabbit words render as emoji when Rabbit char set is active."""
        game = Matrix(40, 20)
        game._char_set_idx = 2  # Rabbit
        # Use a blink-on tick so rabbit emoji are visible
        game._tick_count = BLINK_OFF
        col = game._columns[3]
        col.rabbit_word = "RABBIT"
        col.rabbit_offset = 0
        col.trail_len = max(col.trail_len, len("RABBIT"))
        col.chars = list(range(col.trail_len))
        col.head = 5
        col.speed = 1
        col.delay = 0
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        # "R" maps to 🐰 in RABBIT_LETTER_EMOJI
        assert RABBIT_LETTER_EMOJI["R"] in grid_text


class TestRabbitLetterCell:
    """Tests for Matrix._rabbit_letter_cell method."""

    def test_ascii_set_pads_letter(self):
        """Test that ASCII char set pads letters with a space."""
        game = Matrix(40, 20)
        game._char_set_idx = 0  # Numbers
        assert game._rabbit_letter_cell("R") == "R "

    def test_rabbit_set_maps_known_letter(self):
        """Test that Rabbit char set maps known letters to emoji."""
        game = Matrix(40, 20)
        game._char_set_idx = 2  # Rabbit
        assert game._rabbit_letter_cell("R") == RABBIT_LETTER_EMOJI["R"]

    def test_rabbit_set_unknown_letter_pads(self):
        """Test that Rabbit char set pads unknown letters with a space."""
        game = Matrix(40, 20)
        game._char_set_idx = 2  # Rabbit
        # "Z" is not in RABBIT_LETTER_EMOJI
        assert game._rabbit_letter_cell("Z") == "Z "


class TestBlinkCells:
    """Tests for rabbit emoji blinking animation."""

    def _make_rabbit_game(self):
        """Create a game in Rabbit mode with a rabbit emoji visible."""
        game = Matrix(40, 20)
        game._char_set_idx = 2  # Rabbit
        col = game._columns[0]
        col.rabbit_word = ""
        col.head = 3
        col.speed = 1
        col.delay = 0
        col.trail_len = 12
        # Seed 0 mod 4 = 0 → first entry in head pool = 🐰
        col.chars = [0] * col.trail_len
        return game

    def test_blink_cells_contains_rabbit_emoji(self):
        """Test that BLINK_CELLS includes rabbit and hare emoji."""
        assert "\U0001f430" in BLINK_CELLS  # 🐰
        assert "\U0001f407" in BLINK_CELLS  # 🐇

    def test_rabbit_hidden_during_blink_off(self):
        """Test that rabbit emoji are hidden during blink-off ticks."""
        game = self._make_rabbit_game()
        # Advance to a blink-off tick (tick_count % BLINK_PERIOD < BLINK_OFF)
        game._tick_count = 0  # 0 % 4 == 0 < 1 → hidden
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        for cell in BLINK_CELLS:
            assert cell not in grid_text

    def test_rabbit_visible_during_blink_on(self):
        """Test that rabbit emoji are visible during blink-on ticks."""
        game = self._make_rabbit_game()
        # Advance to a blink-on tick
        game._tick_count = BLINK_OFF  # 1 % 4 == 1 >= 1 → visible
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        found = any(cell in grid_text for cell in BLINK_CELLS)
        assert found

    def test_blink_cycle_alternates(self):
        """Test that blink cycle has correct visible and hidden counts."""
        game = self._make_rabbit_game()
        visible_count = 0
        hidden_count = 0
        for tick in range(BLINK_PERIOD):
            game._tick_count = tick
            frame = game.get_frame()
            grid_text = "".join(frame[:game.height])
            if any(cell in grid_text for cell in BLINK_CELLS):
                visible_count += 1
            else:
                hidden_count += 1
        assert visible_count == BLINK_PERIOD - BLINK_OFF
        assert hidden_count == BLINK_OFF

    def test_non_rabbit_emoji_unaffected(self):
        """Non-rabbit emoji like carrot should not blink."""
        game = self._make_rabbit_game()
        col = game._columns[1]
        col.rabbit_word = ""
        col.head = 8
        col.speed = 1
        col.delay = 0
        col.trail_len = 12
        # Seed 1 mod 5 = 1 → second body entry = 🥕
        # Position i=5 falls in body zone (third=4, 4<=5<8)
        col.chars = [1] * col.trail_len
        game._tick_count = 0  # blink-off tick
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "\U0001f955" in grid_text  # 🥕 still visible


class TestMatrixHandleInput:
    """Tests for Matrix.handle_input (selection + ignored keys)."""

    def test_selection_changes_char_set(self):
        """Test that selection key changes the active char set."""
        game = Matrix(40, 20)
        game.handle_input("s")
        assert game._char_set_idx == 1

    def test_other_keys_ignored(self):
        """Test that non-selection keys do not change char set."""
        game = Matrix(40, 20)
        game.handle_input("h")
        game.handle_input("j")
        assert game._char_set_idx == 0


class TestMatrixGameOver:
    """Tests for Matrix game over state."""

    def test_never_game_over(self):
        """Test that matrix never enters game over state."""
        game = Matrix(40, 20)
        for _ in range(100):
            game.tick()
        assert game.is_game_over() is False

    def test_game_over_frame_returns_frame(self):
        """Test that get_game_over_frame returns a non-empty list."""
        game = Matrix(40, 20)
        frame = game.get_game_over_frame()
        assert isinstance(frame, list)
        assert len(frame) > 0

    def test_game_over_frame_same_as_frame(self):
        """Test that game over frame has same length as regular frame."""
        game = Matrix(40, 20)
        game.tick()
        frame1 = game.get_frame()
        frame2 = game.get_game_over_frame()
        assert len(frame1) == len(frame2)
