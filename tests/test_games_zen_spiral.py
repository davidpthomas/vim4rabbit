"""Tests for vim4rabbit.games.zen_spiral module."""

import pytest
from vim4rabbit.games.zen_spiral import ZenSpiral, SPIRAL_CHARS


class TestZenSpiralInit:
    """Tests for ZenSpiral initialization."""

    def test_default_dimensions(self):
        """Test that normal dimensions are stored correctly."""
        game = ZenSpiral(40, 20)
        assert game.width == 40
        assert game.height == 18

    def test_minimum_dimensions(self):
        """Test that small values are clamped to minimums."""
        game = ZenSpiral(5, 5)
        assert game.width == 10
        assert game.height == 10

    def test_initial_state(self):
        """Test that initial state has zero theta and no points."""
        game = ZenSpiral(40, 20)
        assert game.theta == 0.0
        assert game.points == []
        assert game.is_game_over() is False


class TestZenSpiralTick:
    """Tests for ZenSpiral.tick method."""

    def test_tick_adds_point(self):
        """Test that a single tick adds at least one point."""
        game = ZenSpiral(40, 20)
        game.tick()
        assert len(game.points) >= 1

    def test_multiple_ticks(self):
        """Test that multiple ticks accumulate points."""
        game = ZenSpiral(40, 20)
        for _ in range(10):
            game.tick()
        assert len(game.points) > 1

    def test_theta_advances(self):
        """Test that theta increases after a tick."""
        game = ZenSpiral(40, 20)
        initial_theta = game.theta
        game.tick()
        assert game.theta > initial_theta

    def test_resets_when_out_of_bounds(self):
        """Test that spiral resets gracefully when it exits bounds."""
        game = ZenSpiral(20, 15)
        # Tick many times until spiral exits bounds
        for _ in range(200):
            game.tick()
        # After many ticks, points should have been reset at least once
        # (spiral grows and eventually exits the small buffer)
        # Just verify it doesn't crash and still produces frames
        frame = game.get_frame()
        assert isinstance(frame, list)


class TestZenSpiralGetFrame:
    """Tests for ZenSpiral.get_frame method."""

    def test_frame_dimensions(self):
        """Test that frame has correct number of lines."""
        game = ZenSpiral(40, 20)
        frame = game.get_frame()
        assert len(frame) == game.height + 2

    def test_frame_width(self):
        """Test that grid rows match the game width."""
        game = ZenSpiral(40, 20)
        frame = game.get_frame()
        # Grid rows should be width chars
        assert len(frame[0]) == 40

    def test_frame_has_status_line(self):
        """Test that frame includes cancel and game name in status."""
        game = ZenSpiral(40, 20)
        frame = game.get_frame()
        assert "[c] cancel" in frame[-1]
        assert "Zen Spiral" in frame[-1]

    def test_frame_shows_points(self):
        """Test that spiral characters appear after ticking."""
        game = ZenSpiral(40, 20)
        for _ in range(5):
            game.tick()
        frame = game.get_frame()
        # At least one point should be visible
        grid_text = "".join(frame[:game.height])
        has_spiral_char = any(c in grid_text for c in SPIRAL_CHARS)
        assert has_spiral_char


class TestZenSpiralHandleInput:
    """Tests for ZenSpiral.handle_input (no-op)."""

    def test_handle_input_is_noop(self):
        """Test that handle_input does not change game state."""
        game = ZenSpiral(40, 20)
        game.tick()
        points_before = len(game.points)
        game.handle_input("h")
        assert len(game.points) == points_before


class TestZenSpiralGameOver:
    """Tests for ZenSpiral game over state."""

    def test_never_game_over(self):
        """Test that zen spiral never enters game over state."""
        game = ZenSpiral(40, 20)
        for _ in range(100):
            game.tick()
        assert game.is_game_over() is False

    def test_game_over_frame_returns_frame(self):
        """Test that get_game_over_frame returns a non-empty list."""
        game = ZenSpiral(40, 20)
        frame = game.get_game_over_frame()
        assert isinstance(frame, list)
        assert len(frame) > 0
