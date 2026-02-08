"""Tests for vim4rabbit.games.pong module."""

import pytest
from vim4rabbit.games.pong import Pong, WINNING_SCORE, PADDLE_HEIGHT


class TestPongInit:
    """Tests for Pong initialization."""

    def test_default_dimensions(self):
        game = Pong(60, 30)
        assert game.width == 60
        assert game.height == 24  # height - 6 for scoreboard

    def test_minimum_dimensions(self):
        game = Pong(10, 10)
        assert game.width == 30
        assert game.height == 12

    def test_initial_scores(self):
        game = Pong(60, 30)
        assert game.left_score == 0
        assert game.right_score == 0

    def test_not_game_over_initially(self):
        game = Pong(60, 30)
        assert game.is_game_over() is False

    def test_paddles_centered(self):
        game = Pong(60, 30)
        expected_y = (game.height - game.paddle_h) // 2
        assert game.left_y == expected_y
        assert game.right_y == expected_y

    def test_ball_at_center(self):
        game = Pong(60, 30)
        assert game.ball_x == game.width // 2
        assert game.ball_y == game.height // 2

    def test_paddle_positions(self):
        game = Pong(60, 30)
        assert game.left_x == 1
        assert game.right_x == game.width - 2


class TestPongTick:
    """Tests for Pong.tick method."""

    def test_tick_moves_ball(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        old_x = game.ball_x
        game.tick()
        assert game.ball_x != old_x

    def test_serve_delay(self):
        game = Pong(60, 30)
        game._serve_delay = 2
        old_x = game.ball_x
        game.tick()
        assert game.ball_x == old_x  # ball doesn't move during delay

    def test_ball_bounces_top(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_y = 0
        game.ball_dy = -1
        game.ball_dx = 1
        game.ball_x = game.width // 2  # keep in middle
        game.tick()
        assert game.ball_dy == 1  # bounced

    def test_ball_bounces_bottom(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_y = game.height - 1
        game.ball_dy = 1
        game.ball_dx = 1
        game.ball_x = game.width // 2
        game.tick()
        assert game.ball_dy == -1  # bounced

    def test_does_not_tick_after_game_over(self):
        game = Pong(60, 30)
        game._game_over = True
        old_x = game.ball_x
        game.tick()
        assert game.ball_x == old_x

    def test_left_paddle_hit(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.left_x + 1
        game.ball_y = game.left_y + game.paddle_h // 2
        game.ball_dx = -1
        game.ball_dy = 0
        game.tick()
        assert game.ball_dx == 1  # reversed direction

    def test_right_paddle_hit(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.right_x - 1
        game.ball_y = game.right_y + game.paddle_h // 2
        game.ball_dx = 1
        game.ball_dy = 0
        game.tick()
        assert game.ball_dx == -1  # reversed direction


class TestPongScoring:
    """Tests for scoring mechanics."""

    def test_right_scores_on_left_miss(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.left_x + 1
        game.ball_y = 0  # above left paddle
        game.left_y = game.height - game.paddle_h  # paddle at bottom
        game.ball_dx = -1
        game.ball_dy = 0
        game.tick()
        assert game.right_score == 1

    def test_left_scores_on_right_miss(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.right_x - 1
        game.ball_y = 0  # above right paddle
        game.right_y = game.height - game.paddle_h  # paddle at bottom
        game.ball_dx = 1
        game.ball_dy = 0
        game.tick()
        assert game.left_score == 1

    def test_game_over_on_winning_score(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.left_score = WINNING_SCORE - 1
        game.ball_x = game.right_x - 1
        game.ball_y = 0
        game.right_y = game.height - game.paddle_h
        game.ball_dx = 1
        game.ball_dy = 0
        game.tick()
        assert game.is_game_over() is True
        assert game._winner == "left"

    def test_ai_wins(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.right_score = WINNING_SCORE - 1
        game.ball_x = game.left_x + 1
        game.ball_y = 0
        game.left_y = game.height - game.paddle_h
        game.ball_dx = -1
        game.ball_dy = 0
        game.tick()
        assert game.is_game_over() is True
        assert game._winner == "right"

    def test_ball_resets_after_score(self):
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.left_x + 1
        game.ball_y = 0
        game.left_y = game.height - game.paddle_h
        game.ball_dx = -1
        game.ball_dy = 0
        game.tick()
        # Ball should be reset to center
        assert game.ball_x == game.width // 2
        assert game.ball_y == game.height // 2


class TestPongHandleInput:
    """Tests for Pong.handle_input."""

    def test_move_down(self):
        game = Pong(60, 30)
        old_y = game.left_y
        game.handle_input("j")
        assert game.left_y == old_y + 1

    def test_move_up(self):
        game = Pong(60, 30)
        game.left_y = 5
        game.handle_input("k")
        assert game.left_y == 4

    def test_cannot_move_above_top(self):
        game = Pong(60, 30)
        game.left_y = 0
        game.handle_input("k")
        assert game.left_y == 0

    def test_cannot_move_below_bottom(self):
        game = Pong(60, 30)
        game.left_y = game.height - game.paddle_h
        game.handle_input("j")
        assert game.left_y == game.height - game.paddle_h

    def test_invalid_key_ignored(self):
        game = Pong(60, 30)
        old_y = game.left_y
        game.handle_input("x")
        assert game.left_y == old_y


class TestPongGetFrame:
    """Tests for Pong.get_frame method."""

    def test_frame_is_list_of_strings(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        assert isinstance(frame, list)
        assert all(isinstance(line, str) for line in frame)

    def test_frame_has_correct_rows(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        # height grid rows + blank + score line + score bar + status = height + 4
        assert len(frame) == game.height + 4

    def test_frame_shows_ball(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "*" in grid_text

    def test_frame_shows_paddles(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "|" in grid_text

    def test_frame_shows_net(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert ":" in grid_text

    def test_frame_has_status_line(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        assert "Pong" in frame[-1]
        assert "[c]" in frame[-1]

    def test_frame_has_score_display(self):
        game = Pong(60, 30)
        frame = game.get_frame()
        full_text = "\n".join(frame)
        assert "YOU" in full_text
        assert "AI" in full_text


class TestPongGameOver:
    """Tests for Pong game over state."""

    def test_game_over_frame_left_wins(self):
        game = Pong(60, 30)
        game._game_over = True
        game._winner = "left"
        game.left_score = 5
        game.right_score = 3
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "YOU WIN" in full_text
        assert "[c]" in full_text

    def test_game_over_frame_right_wins(self):
        game = Pong(60, 30)
        game._game_over = True
        game._winner = "right"
        game.left_score = 2
        game.right_score = 5
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "AI WINS" in full_text
        assert "[c]" in full_text


class TestPongAI:
    """Tests for AI paddle behavior."""

    def test_deflect_top_of_paddle(self):
        """Test ball deflects upward when hitting top of paddle."""
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.left_x + 1
        game.ball_y = game.left_y  # top of paddle
        game.ball_dx = -1
        game.ball_dy = 0
        game.tick()
        assert game.ball_dy == -1

    def test_deflect_bottom_of_paddle(self):
        """Test ball deflects downward when hitting bottom of paddle."""
        game = Pong(60, 30)
        game._serve_delay = 0
        game.ball_x = game.left_x + 1
        game.ball_y = game.left_y + game.paddle_h - 1  # bottom of paddle
        game.ball_dx = -1
        game.ball_dy = 0
        game.tick()
        assert game.ball_dy == 1

    def test_ai_tracks_ball_down(self):
        game = Pong(60, 30)
        game.right_y = 0
        game.ball_y = game.height - 1
        game.ball_dx = 1
        game._serve_delay = 0
        old_y = game.right_y
        game._move_ai()
        assert game.right_y > old_y

    def test_ai_tracks_ball_up(self):
        game = Pong(60, 30)
        game.right_y = game.height - game.paddle_h
        game.ball_y = 0
        game.ball_dx = 1
        game._serve_delay = 0
        old_y = game.right_y
        game._move_ai()
        assert game.right_y < old_y
