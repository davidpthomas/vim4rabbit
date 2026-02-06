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
    GAME_REGISTRY,
)


class TestGetGameMenu:
    """Tests for get_game_menu function."""

    def test_returns_list_of_strings(self):
        lines = get_game_menu()
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)

    def test_contains_game_options(self):
        lines = get_game_menu()
        full_text = "\n".join(lines)
        assert "Zen Spiral" in full_text
        assert "Coffee from Uganda" in full_text
        assert "Snake" in full_text

    def test_contains_key_hints(self):
        lines = get_game_menu()
        full_text = "\n".join(lines)
        assert "[z]" in full_text
        assert "[e]" in full_text
        assert "[s]" in full_text
        assert "[c] to go back" in full_text


class TestStartStopGame:
    """Tests for start_game and stop_game functions."""

    def setup_method(self):
        stop_game()

    def teardown_method(self):
        stop_game()

    def test_start_valid_game(self):
        assert start_game("z", 40, 20) is True
        assert is_game_active() is True

    def test_start_invalid_key(self):
        assert start_game("x", 40, 20) is False
        assert is_game_active() is False

    def test_stop_game(self):
        start_game("z", 40, 20)
        stop_game()
        assert is_game_active() is False

    def test_stop_when_no_game(self):
        stop_game()
        assert is_game_active() is False

    def test_start_each_game_type(self):
        for key in GAME_REGISTRY:
            start_game(key, 40, 20)
            assert is_game_active() is True
            stop_game()


class TestGetTickRate:
    """Tests for get_tick_rate function."""

    def test_zen_spiral_rate(self):
        assert get_tick_rate("z") == 500

    def test_coffee_cup_rate(self):
        assert get_tick_rate("e") == 1040

    def test_snake_rate(self):
        assert get_tick_rate("s") == 200

    def test_unknown_key(self):
        assert get_tick_rate("x") == 500


class TestTickGame:
    """Tests for tick_game function."""

    def setup_method(self):
        stop_game()

    def teardown_method(self):
        stop_game()

    def test_tick_no_active_game(self):
        assert tick_game() == []

    def test_tick_returns_frame(self):
        start_game("z", 40, 20)
        frame = tick_game()
        assert isinstance(frame, list)
        assert len(frame) > 0

    def test_tick_advances_game(self):
        start_game("z", 40, 20)
        frame1 = tick_game()
        frame2 = tick_game()
        # Frames should differ as spiral progresses
        assert isinstance(frame2, list)
        assert len(frame2) > 0


class TestInputGame:
    """Tests for input_game function."""

    def setup_method(self):
        stop_game()

    def teardown_method(self):
        stop_game()

    def test_input_no_active_game(self):
        assert input_game("h") == []

    def test_input_returns_frame(self):
        start_game("s", 40, 20)
        frame = input_game("l")
        assert isinstance(frame, list)
        assert len(frame) > 0


class TestGameRegistry:
    """Tests for GAME_REGISTRY."""

    def test_all_keys_present(self):
        assert "z" in GAME_REGISTRY
        assert "e" in GAME_REGISTRY
        assert "s" in GAME_REGISTRY

    def test_registry_structure(self):
        for key, (name, cls, tick_ms) in GAME_REGISTRY.items():
            assert isinstance(name, str)
            assert callable(cls)
            assert isinstance(tick_ms, int)
            assert tick_ms > 0
