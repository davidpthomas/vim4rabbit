"""Tests for vim4rabbit.games.coffee_cup module."""

import pytest
from vim4rabbit.games.coffee_cup import CoffeeCup, FILL_CHARS, CUP_WIDTH


class TestCoffeeCupInit:
    """Tests for CoffeeCup initialization."""

    def test_default_dimensions(self):
        game = CoffeeCup(40, 20)
        assert game.width == 40
        assert game.height == 20

    def test_minimum_dimensions(self):
        game = CoffeeCup(10, 5)
        assert game.width == 30
        assert game.height == 15

    def test_initial_state(self):
        game = CoffeeCup(40, 20)
        assert game.fill_level == 0
        assert game.steam_ticks == 0
        assert game.is_game_over() is False


class TestCoffeeCupTick:
    """Tests for CoffeeCup.tick method."""

    def test_tick_fills_one_row(self):
        game = CoffeeCup(40, 20)
        game.tick()
        assert game.fill_level == 1

    def test_fills_incrementally(self):
        game = CoffeeCup(40, 20)
        for i in range(1, 5):
            game.tick()
            assert game.fill_level == i

    def test_starts_steam_when_full(self):
        game = CoffeeCup(40, 20)
        # Fill all rows
        for _ in range(game.interior_rows):
            game.tick()
        assert game.fill_level == game.interior_rows
        # One more tick starts steam
        game.tick()
        assert game.steam_ticks == 1

    def test_steam_advances(self):
        game = CoffeeCup(40, 20)
        for _ in range(game.interior_rows):
            game.tick()
        game.tick()  # steam_ticks = 1
        game.tick()  # steam_ticks = 2
        assert game.steam_ticks == 2

    def test_resets_after_steam(self):
        game = CoffeeCup(40, 20)
        # Fill up
        for _ in range(game.interior_rows):
            game.tick()
        # Trigger steam and wait for it to finish
        for _ in range(game.steam_max + 1):
            game.tick()
        assert game.fill_level == 0
        assert game.steam_ticks == 0


class TestCoffeeCupGetFrame:
    """Tests for CoffeeCup.get_frame method."""

    def test_frame_is_list_of_strings(self):
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        assert isinstance(frame, list)
        assert all(isinstance(line, str) for line in frame)

    def test_frame_has_cup_outline(self):
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        full_text = "\n".join(frame)
        assert ".---" in full_text  # rim
        assert "'---" in full_text  # base

    def test_frame_has_status_line(self):
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        assert "Coffee Cup" in frame[-1]
        assert "[c]" in frame[-1]

    def test_empty_cup_has_empty_interior(self):
        game = CoffeeCup(40, 20)
        frame = game.get_frame()
        # Find interior rows (between rim and base)
        for line in frame:
            if line.startswith("    |") and line.endswith("|"):
                interior = line[5:-1]
                assert interior.strip() == ""

    def test_filled_rows_have_fill_chars(self):
        game = CoffeeCup(40, 20)
        game.tick()
        game.tick()
        frame = game.get_frame()
        # Find interior rows with fill
        filled_rows = []
        for line in frame:
            if line.startswith("    |") and line.endswith("|"):
                interior = line[5:-1]
                if interior.strip():
                    filled_rows.append(interior)
        assert len(filled_rows) == 2

    def test_steam_frame_shows_yummm(self):
        game = CoffeeCup(40, 20)
        for _ in range(game.interior_rows):
            game.tick()
        game.tick()  # start steam
        frame = game.get_frame()
        full_text = "\n".join(frame)
        assert "Yummm!!!" in full_text


class TestCoffeeCupHandleInput:
    """Tests for CoffeeCup.handle_input (no-op)."""

    def test_handle_input_is_noop(self):
        game = CoffeeCup(40, 20)
        level_before = game.fill_level
        game.handle_input("h")
        assert game.fill_level == level_before


class TestCoffeeCupGameOver:
    """Tests for CoffeeCup game over state."""

    def test_never_game_over(self):
        game = CoffeeCup(40, 20)
        for _ in range(50):
            game.tick()
        assert game.is_game_over() is False

    def test_game_over_frame_returns_frame(self):
        game = CoffeeCup(40, 20)
        frame = game.get_game_over_frame()
        assert isinstance(frame, list)
        assert len(frame) > 0
