"""Tests for vim4rabbit.games.wargames module."""

import pytest
from vim4rabbit.games.wargames import WarGames, PASSWORD, MAX_LAUNCHES, COUNTRIES


class TestWarGamesInit:
    """Tests for WarGames initialization."""

    def test_default_dimensions(self):
        """Test that normal dimensions are stored correctly."""
        game = WarGames(60, 30)
        assert game.width == 60
        assert game.height == 26  # height - 4

    def test_minimum_dimensions(self):
        """Test that small values are clamped to minimums."""
        game = WarGames(10, 10)
        assert game.width == 50
        assert game.height == 16

    def test_starts_in_password_phase(self):
        """Test that game begins in password entry phase."""
        game = WarGames(60, 30)
        assert game.phase == "password"

    def test_not_game_over_initially(self):
        """Test that game is not over at start."""
        game = WarGames(60, 30)
        assert game.is_game_over() is False

    def test_no_launches_initially(self):
        """Test that no missiles have been launched at start."""
        game = WarGames(60, 30)
        assert game.launches == 0
        assert game.human_targets == []
        assert game.ai_targets == []


class TestWarGamesPassword:
    """Tests for password entry phase."""

    def test_correct_password_advances(self):
        """Test that entering correct password advances to globe phase."""
        game = WarGames(60, 30)
        for ch in PASSWORD:
            game.handle_input(ch)
        assert game.phase == "globe"

    def test_wrong_password_resets(self):
        """Test that wrong password clears typed text and shows error."""
        game = WarGames(60, 30)
        for ch in "abcdef":
            game.handle_input(ch)
        assert game.phase == "password"
        assert game.typed == ""
        assert game.pw_error is True

    def test_partial_password(self):
        """Test that partial input stays in password phase."""
        game = WarGames(60, 30)
        game.handle_input("j")
        game.handle_input("o")
        assert game.phase == "password"
        assert game.typed == "jo"

    def test_password_is_case_insensitive(self):
        """Test that uppercase password is accepted."""
        game = WarGames(60, 30)
        for ch in "JOSHUA":
            game.handle_input(ch)
        assert game.phase == "globe"

    def test_non_alpha_ignored(self):
        """Test that non-alphabetic characters are ignored."""
        game = WarGames(60, 30)
        game.handle_input("1")
        game.handle_input("!")
        assert game.typed == ""


class TestWarGamesLaunching:
    """Tests for missile launching."""

    def _enter_password(self, game):
        """Enter the correct password to advance past the password phase."""
        for ch in PASSWORD:
            game.handle_input(ch)

    def test_launch_missile(self):
        """Test that pressing x launches a missile."""
        game = WarGames(60, 30)
        self._enter_password(game)
        game.handle_input("x")
        assert game.launches == 1
        assert len(game.human_targets) == 1
        assert game.phase == "missile"

    def test_cannot_launch_during_password(self):
        """Test that x key is ignored during password phase."""
        game = WarGames(60, 30)
        game.handle_input("x")
        assert game.launches == 0

    def test_cannot_launch_during_animation(self):
        """Test that x key is ignored during missile animation."""
        game = WarGames(60, 30)
        self._enter_password(game)
        game.handle_input("x")
        assert game.phase == "missile"
        game.handle_input("x")  # should be ignored
        assert game.launches == 1

    def test_ai_responds_after_human(self):
        """Test that AI launches a counter-missile after human animation."""
        game = WarGames(60, 30)
        self._enter_password(game)
        game.handle_input("x")
        # Run through human animation
        for _ in range(5):
            game.tick()
        assert len(game.ai_targets) == 1
        assert game._anim_who == "ai"

    def test_game_over_after_max_launches(self):
        """Test that game ends after maximum launches are exhausted."""
        game = WarGames(60, 30)
        self._enter_password(game)
        for _ in range(MAX_LAUNCHES):
            game.handle_input("x")
            # Human animation (5 ticks)
            for _ in range(5):
                game.tick()
            # AI animation (5 ticks)
            for _ in range(5):
                game.tick()
        assert game.is_game_over() is True

    def test_returns_to_globe_between_launches(self):
        """Test that game returns to globe phase after each round."""
        game = WarGames(60, 30)
        self._enter_password(game)
        game.handle_input("x")
        # Human animation
        for _ in range(5):
            game.tick()
        # AI animation
        for _ in range(5):
            game.tick()
        assert game.phase == "globe"

    def test_targets_are_from_countries(self):
        """Test that launched targets are from the country list."""
        game = WarGames(60, 30)
        self._enter_password(game)
        game.handle_input("x")
        assert game.human_targets[0] in COUNTRIES


class TestWarGamesTick:
    """Tests for tick behavior."""

    def test_tick_noop_during_password(self):
        """Test that tick has no effect during password phase."""
        game = WarGames(60, 30)
        game.tick()
        assert game.phase == "password"

    def test_tick_noop_during_globe(self):
        """Test that tick has no effect during globe phase."""
        game = WarGames(60, 30)
        for ch in PASSWORD:
            game.handle_input(ch)
        game.tick()
        assert game.phase == "globe"

    def test_tick_noop_after_game_over(self):
        """Test that tick has no effect after game over."""
        game = WarGames(60, 30)
        game._game_over = True
        game.tick()
        assert game._game_over is True


class TestWarGamesGetFrame:
    """Tests for frame rendering."""

    def test_password_frame(self):
        """Test that password frame shows login prompt."""
        game = WarGames(60, 30)
        frame = game.get_frame()
        assert isinstance(frame, list)
        full = "\n".join(frame)
        assert "PROFESSOR FALKEN" in full
        assert "PASSWORD" in full
        assert "[c] cancel" in full

    def test_globe_frame(self):
        """Test that globe frame shows WOPR and launch controls."""
        game = WarGames(60, 30)
        for ch in PASSWORD:
            game.handle_input(ch)
        frame = game.get_frame()
        full = "\n".join(frame)
        assert "W.O.P.R." in full
        assert "DEFCON" in full
        assert "[x]" in full
        assert "[c] cancel" in full

    def test_missile_frame(self):
        """Test that missile frame shows launching animation."""
        game = WarGames(60, 30)
        for ch in PASSWORD:
            game.handle_input(ch)
        game.handle_input("x")
        frame = game.get_frame()
        full = "\n".join(frame)
        assert "LAUNCHING" in full
        assert "[c] cancel" in full

    def test_game_over_frame(self):
        """Test that game over frame shows classic WarGames quote."""
        game = WarGames(60, 30)
        game._game_over = True
        frame = game.get_game_over_frame()
        full = "\n".join(frame)
        assert "ONLY WINNING MOVE" in full
        assert "NOT TO PLAY" in full
        assert "CHESS" in full
        assert "[o]" in full
        assert "[c] cancel" in full

    def test_password_error_shown(self):
        """Test that incorrect password shows error message."""
        game = WarGames(60, 30)
        for ch in "abcdef":
            game.handle_input(ch)
        frame = game.get_frame()
        full = "\n".join(frame)
        assert "NOT RECOGNIZED" in full

    def test_defcon_decreases(self):
        """Test that DEFCON level decreases after a launch round."""
        game = WarGames(60, 30)
        for ch in PASSWORD:
            game.handle_input(ch)
        frame = game.get_frame()
        assert any("DEFCON: 5" in line for line in frame)
        game.handle_input("x")
        # Complete human + AI animation
        for _ in range(10):
            game.tick()
        frame = game.get_frame()
        assert any("DEFCON: 4" in line for line in frame)


class TestWarGamesGameOver:
    """Tests for game over state."""

    def test_game_over_frame_has_classic_quote(self):
        """Test that game over frame includes the classic movie quotes."""
        game = WarGames(60, 30)
        game._game_over = True
        frame = game.get_game_over_frame()
        full = "\n".join(frame)
        assert "STRANGE GAME" in full
        assert "WINNER: NONE" in full

    def test_input_ignored_after_game_over(self):
        """Test that launch input is ignored after game over."""
        game = WarGames(60, 30)
        game._game_over = True
        game.handle_input("x")
        assert game.launches == 0

    def test_chess_phase(self):
        """Test pressing 'o' after game over shows chess board screen."""
        game = WarGames(60, 30)
        game._game_over = True
        game.handle_input("o")
        assert game.phase == "chess"
        frame = game.get_game_over_frame()
        full = "\n".join(frame)
        assert "Coming Soon" in full
        assert "[c] cancel" in full
        # Verify chessboard elements
        assert "♔" in full
        assert "♚" in full

    def test_chess_only_once(self):
        """Test pressing 'o' again while already in chess phase is a no-op."""
        game = WarGames(60, 30)
        game._game_over = True
        game.handle_input("o")
        assert game.phase == "chess"
        game.handle_input("o")
        assert game.phase == "chess"


class TestWarGamesAIMissileFrame:
    """Tests for AI missile animation rendering."""

    def _launch_and_get_to_ai_anim(self, game):
        """Enter password, launch, and tick through human animation."""
        for ch in PASSWORD:
            game.handle_input(ch)
        game.handle_input("x")
        for _ in range(5):
            game.tick()

    def test_ai_missile_frame_shows_wopr(self):
        """Test missile frame during AI animation shows WOPR label."""
        game = WarGames(60, 30)
        self._launch_and_get_to_ai_anim(game)
        assert game._anim_who == "ai"
        frame = game.get_frame()
        full = "\n".join(frame)
        assert "WOPR" in full
        assert "LAUNCHING" in full

    def test_ai_targets_shown_in_missile_frame(self):
        """Test that AI target log lines appear in the missile frame."""
        game = WarGames(60, 30)
        self._launch_and_get_to_ai_anim(game)
        frame = game.get_frame()
        full = "\n".join(frame)
        assert "WOPR >> MISSILE #1" in full


class TestWarGamesPoolExhausted:
    """Tests for when the country pool is exhausted."""

    def test_fire_ai_with_empty_pool(self):
        """Test AI picks a random country when pool is empty."""
        game = WarGames(60, 30)
        game._pool.clear()
        game._fire_ai()
        assert len(game.ai_targets) == 1
        assert game.ai_targets[0] in COUNTRIES
