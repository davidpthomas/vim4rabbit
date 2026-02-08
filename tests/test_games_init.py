"""Tests for vim4rabbit.games module (game manager)."""

import pytest
from vim4rabbit.games import (
    get_game_menu,
    start_game,
    stop_game,
    is_game_active,
    get_tick_rate,
    tick_game,
    input_game,
    get_game_match_patterns,
    GAME_REGISTRY,
)


class TestGetGameMenu:
    """Tests for get_game_menu function."""

    def test_returns_list_of_strings(self):
        """Test that menu returns a list of strings."""
        lines = get_game_menu()
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)

    def test_contains_game_options(self):
        """Test that menu lists all available games."""
        lines = get_game_menu()
        full_text = "\n".join(lines)
        assert "Zen Spiral" in full_text
        assert "Coffee Break!" in full_text
        assert "Snake" in full_text
        assert "Global Thermonuclear War" in full_text
        assert "Enter the Matrix" in full_text

    def test_contains_key_hints(self):
        """Test that menu shows key bindings for each game."""
        lines = get_game_menu()
        full_text = "\n".join(lines)
        assert "[z]" in full_text
        assert "[b]" in full_text
        assert "[s]" in full_text
        assert "[w]" in full_text
        assert "[m]" in full_text
        assert "[c] to go back" in full_text


class TestStartStopGame:
    """Tests for start_game and stop_game functions."""

    def setup_method(self):
        """Reset game state before each test."""
        stop_game()

    def teardown_method(self):
        """Reset game state after each test."""
        stop_game()

    def test_start_valid_game(self):
        """Test that a valid key starts a game."""
        assert start_game("z", 40, 20) is True
        assert is_game_active() is True

    def test_start_invalid_key(self):
        """Test that an invalid key does not start a game."""
        assert start_game("x", 40, 20) is False
        assert is_game_active() is False

    def test_stop_game(self):
        """Test that stopping a game deactivates it."""
        start_game("z", 40, 20)
        stop_game()
        assert is_game_active() is False

    def test_stop_when_no_game(self):
        """Test that stopping with no active game is a no-op."""
        stop_game()
        assert is_game_active() is False

    def test_start_each_game_type(self):
        """Test that every registered game key starts successfully."""
        for key in GAME_REGISTRY:
            start_game(key, 40, 20)
            assert is_game_active() is True
            stop_game()


class TestGetTickRate:
    """Tests for get_tick_rate function."""

    def test_zen_spiral_rate(self):
        """Test that zen spiral has 500ms tick rate."""
        assert get_tick_rate("z") == 500

    def test_coffee_cup_rate(self):
        """Test that coffee cup has 1040ms tick rate."""
        assert get_tick_rate("b") == 1040

    def test_snake_rate(self):
        """Test that snake has 200ms tick rate."""
        assert get_tick_rate("s") == 200

    def test_unknown_key(self):
        """Test that unknown key returns default 500ms tick rate."""
        assert get_tick_rate("x") == 500


class TestTickGame:
    """Tests for tick_game function."""

    def setup_method(self):
        """Reset game state before each test."""
        stop_game()

    def teardown_method(self):
        """Reset game state after each test."""
        stop_game()

    def test_tick_no_active_game(self):
        """Test that tick returns empty list when no game is active."""
        assert tick_game() == []

    def test_tick_returns_frame(self):
        """Test that tick returns a non-empty frame list."""
        start_game("z", 40, 20)
        frame = tick_game()
        assert isinstance(frame, list)
        assert len(frame) > 0

    def test_tick_advances_game(self):
        """Test that successive ticks produce valid frames."""
        start_game("z", 40, 20)
        frame1 = tick_game()
        frame2 = tick_game()
        # Frames should differ as spiral progresses
        assert isinstance(frame2, list)
        assert len(frame2) > 0


class TestInputGame:
    """Tests for input_game function."""

    def setup_method(self):
        """Reset game state before each test."""
        stop_game()

    def teardown_method(self):
        """Reset game state after each test."""
        stop_game()

    def test_input_no_active_game(self):
        """Test that input returns empty list when no game is active."""
        assert input_game("h") == []

    def test_input_returns_frame(self):
        """Test that input returns a non-empty frame list."""
        start_game("s", 40, 20)
        frame = input_game("l")
        assert isinstance(frame, list)
        assert len(frame) > 0


class TestGameOverFrames:
    """Tests for game over frame returns in tick_game and input_game."""

    def setup_method(self):
        """Reset game state before each test."""
        stop_game()

    def teardown_method(self):
        """Reset game state after each test."""
        stop_game()

    def test_tick_game_returns_game_over_frame(self):
        """Test tick_game returns game over frame when game ends."""
        start_game("s", 40, 20)
        # Force game over on the snake instance
        import vim4rabbit.games as gm
        gm._active_game._game_over = True
        frame = tick_game()
        full = "\n".join(frame)
        assert "GAME OVER" in full

    def test_input_game_returns_game_over_frame(self):
        """Test input_game returns game over frame when game ends."""
        start_game("s", 40, 20)
        import vim4rabbit.games as gm
        gm._active_game._game_over = True
        frame = input_game("l")
        full = "\n".join(frame)
        assert "GAME OVER" in full


class TestGetGameMatchPatterns:
    """Tests for get_game_match_patterns function."""

    def setup_method(self):
        """Reset game state before each test."""
        stop_game()

    def teardown_method(self):
        """Reset game state after each test."""
        stop_game()

    def test_no_active_game_returns_empty(self):
        """Test that no active game returns empty pattern list."""
        assert get_game_match_patterns() == []

    def test_game_without_patterns_returns_empty(self):
        """Test that a game without patterns returns empty list."""
        start_game("z", 40, 20)
        assert get_game_match_patterns() == []

    def test_matrix_returns_patterns(self):
        """Test that matrix game returns four highlight patterns."""
        start_game("m", 40, 20)
        patterns = get_game_match_patterns()
        assert len(patterns) == 4
        groups = [p[0] for p in patterns]
        assert "MatrixTrail" in groups
        assert "MatrixBody" in groups
        assert "MatrixHead" in groups
        assert "MatrixWhite" in groups

    def test_matrix_patterns_are_valid_vim_regex(self):
        """Test that matrix patterns use bracket or alternation syntax."""
        start_game("m", 40, 20)
        for group, pattern in get_game_match_patterns():
            is_bracket = pattern.startswith("[") and pattern.endswith("]")
            is_alternation = (pattern.startswith("\\%(")
                              and pattern.endswith("\\)"))
            assert is_bracket or is_alternation


class TestGameRegistry:
    """Tests for GAME_REGISTRY."""

    def test_all_keys_present(self):
        """Test that all expected game keys are registered."""
        assert "z" in GAME_REGISTRY
        assert "b" in GAME_REGISTRY
        assert "s" in GAME_REGISTRY
        assert "w" in GAME_REGISTRY
        assert "m" in GAME_REGISTRY

    def test_registry_structure(self):
        """Test that each registry entry has name, class, and tick rate."""
        for key, (name, cls, tick_ms) in GAME_REGISTRY.items():
            assert isinstance(name, str)
            assert callable(cls)
            assert isinstance(tick_ms, int)
            assert tick_ms > 0


class TestUniformCancelUX:
    """Tests for uniform [c] cancel status bar across all games."""

    def setup_method(self):
        """Reset game state before each test."""
        stop_game()

    def teardown_method(self):
        """Reset game state after each test."""
        stop_game()

    @pytest.mark.parametrize("key", list(GAME_REGISTRY.keys()))
    def test_frame_ends_with_cancel_status_bar(self, key):
        """Every game's frame should end with a pipe-delimited status bar
        containing the game name and [c] cancel."""
        start_game(key, 60, 30)
        frame = tick_game()
        assert len(frame) > 0
        last_line = frame[-1]
        assert "[c] cancel" in last_line
        assert "|" in last_line
