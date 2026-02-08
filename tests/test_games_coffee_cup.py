"""Tests for vim4rabbit.games.coffee_cup module."""

import pytest
from vim4rabbit.games.coffee_cup import CoffeeCup, FILL_CHARS, CUP_WIDTH


class TestCoffeeCupInit:
    """Tests for CoffeeCup initialization."""

    def test_default_dimensions(self):
        """Test that normal dimensions are stored correctly."""
        game = CoffeeCup(40, 20)
        assert game.width == 40
        assert game.height == 20

    def test_minimum_dimensions(self):
        """Test that small values are clamped to minimums."""
        game = CoffeeCup(10, 5)
        assert game.width == 30
        assert game.height == 15

    def test_initial_state(self):
        """Test that cup starts full with no steam."""
        game = CoffeeCup(40, 20)
        assert game.fill_level == game.interior_rows
        assert game.steam_ticks == 0
        assert game.is_game_over() is False


class TestCoffeeCupTick:
    """Tests for CoffeeCup.tick method."""

    def test_tick_drains_one_row(self):
        """Test that one tick drains one row of coffee."""
        game = CoffeeCup(40, 20)
        game.tick()
        assert game.fill_level == game.interior_rows - 1

    def test_drains_incrementally(self):
        """Test that fill level decreases by one each tick."""
        game = CoffeeCup(40, 20)
        for i in range(1, 5):
            game.tick()
            assert game.fill_level == game.interior_rows - i

    def test_refills_and_steams_when_empty(self):
        """Test that cup refills and shows steam once fully drained."""
        game = CoffeeCup(40, 20)
        # Drain all rows
        for _ in range(game.interior_rows):
            game.tick()
        assert game.fill_level == game.interior_rows
        assert game.steam_ticks == 1

    def test_steam_advances(self):
        """Test that steam tick counter increments while steaming."""
        game = CoffeeCup(40, 20)
        for _ in range(game.interior_rows):
            game.tick()
        # steam_ticks = 1, tick again
        game.tick()  # steam_ticks = 2
        assert game.steam_ticks == 2

    def test_resets_after_steam(self):
        """Test that draining resumes after steam phase ends."""
        game = CoffeeCup(40, 20)
        # Drain completely
        for _ in range(game.interior_rows):
            game.tick()
        # Now full again with steam; wait for steam to finish
        for _ in range(game.steam_max):
            game.tick()
        assert game.steam_ticks == 0
        # Next tick should drain
        game.tick()
        assert game.fill_level == game.interior_rows - 1


class TestCoffeeCupGetFrame:
    """Tests for CoffeeCup.get_frame method."""

    def test_frame_is_list_of_strings(self):
        """Test that frame returns a list of strings."""
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        assert isinstance(frame, list)
        assert all(isinstance(line, str) for line in frame)

    def test_frame_has_cup_outline(self):
        """Test that frame contains cup rim and base markers."""
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        full_text = "\n".join(frame)
        assert ".---" in full_text  # rim
        assert "'---" in full_text  # base

    def test_frame_has_status_line(self):
        """Test that frame includes title and cancel in status line."""
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        full_text = "\n".join(frame)
        assert "Coffee from Uganda!" in full_text
        assert "Coffee Break!" in full_text
        assert "[c] cancel" in full_text

    def test_full_cup_has_filled_interior(self):
        """Test that all interior rows are filled when cup is full."""
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        filled_rows = []
        for line in frame:
            stripped = line.strip()
            # Find cup interior between last |...| pair
            if stripped.endswith("|"):
                last = len(stripped) - 1
                second = stripped.rfind("|", 0, last)
                if second >= 0 and (last - second - 1) == CUP_WIDTH:
                    interior = stripped[second + 1:last]
                    if interior.strip():
                        filled_rows.append(interior)
        assert len(filled_rows) == game.interior_rows

    def test_drained_rows_are_empty(self):
        """Test that drained rows have empty interiors."""
        game = CoffeeCup(40, 20)
        game.tick()
        game.tick()
        frame = game.get_frame()
        empty_rows = []
        for line in frame:
            stripped = line.strip()
            if stripped.endswith("|"):
                last = len(stripped) - 1
                second = stripped.rfind("|", 0, last)
                if second >= 0 and (last - second - 1) == CUP_WIDTH:
                    interior = stripped[second + 1:last]
                    if not interior.strip():
                        empty_rows.append(interior)
        assert len(empty_rows) == 2

    def test_steam_frame_shows_sip(self):
        """Test that steam phase frame contains sip indicator."""
        game = CoffeeCup(40, 20)
        for _ in range(game.interior_rows):
            game.tick()
        # Now full with steam
        frame = game.get_frame()
        full_text = "\n".join(frame)
        assert "*sip*" in full_text


class TestCoffeeCupHandleInput:
    """Tests for CoffeeCup.handle_input (no-op)."""

    def test_handle_input_is_noop(self):
        """Test that handle_input does not change fill level."""
        game = CoffeeCup(40, 20)
        level_before = game.fill_level
        game.handle_input("h")
        assert game.fill_level == level_before


class TestCoffeeCupGameOver:
    """Tests for CoffeeCup game over state."""

    def test_never_game_over(self):
        """Test that coffee cup never enters game over state."""
        game = CoffeeCup(40, 20)
        for _ in range(50):
            game.tick()
        assert game.is_game_over() is False

    def test_game_over_frame_returns_frame(self):
        """Test that get_game_over_frame returns a non-empty list."""
        game = CoffeeCup(40, 20)
        frame = game.get_game_over_frame()
        assert isinstance(frame, list)
        assert len(frame) > 0
