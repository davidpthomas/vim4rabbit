"""Tests for vim4rabbit.games.rabbit module."""

import pytest
from vim4rabbit.games.rabbit import (
    Snake, DIRECTIONS, WASD_MAP, INITIAL_PELLETS, GROW_ON_EAT,
    CELL_EMPTY, CELL_HEAD, CELL_TAIL, PELLET_EMOJIS,
)


class TestSnakeInit:
    """Tests for Snake initialization."""

    def test_default_dimensions(self):
        """Test that normal dimensions are stored correctly."""
        game = Snake(40, 22)
        assert game.width == 20  # 40 // 2 (2 cols per cell)
        assert game.height == 20  # height - 2 for status

    def test_minimum_dimensions(self):
        """Test that small values are clamped to minimums."""
        game = Snake(5, 5)
        assert game.width == 10  # min 10 cells
        assert game.height == 10

    def test_initial_snake_length(self):
        """Test that snake starts with length 3."""
        game = Snake(40, 22)
        assert len(game.snake) == 3

    def test_initial_pellet_count(self):
        """Test that initial pellet count matches constant."""
        game = Snake(40, 22)
        assert len(game.pellets) == INITIAL_PELLETS

    def test_initial_direction(self):
        """Test that snake starts moving right."""
        game = Snake(40, 22)
        assert game.direction == "l"  # moving right

    def test_initial_score(self):
        """Test that score starts at zero."""
        game = Snake(40, 22)
        assert game.score == 0

    def test_not_game_over_initially(self):
        """Test that game is not over at start."""
        game = Snake(40, 22)
        assert game.is_game_over() is False


class TestSnakeTick:
    """Tests for Snake.tick method."""

    def test_tick_moves_head(self):
        """Test that a tick moves the snake head."""
        game = Snake(40, 22)
        old_head = game.snake[0]
        game.tick()
        new_head = game.snake[0]
        assert old_head != new_head

    def test_tick_maintains_length(self):
        """Test that snake length stays the same when not eating."""
        game = Snake(40, 22)
        initial_len = len(game.snake)
        # Remove all pellets to prevent eating
        game.pellets = {}
        game.tick()
        assert len(game.snake) == initial_len

    def test_tick_moves_right(self):
        """Test that snake moves right when direction is 'l'."""
        game = Snake(40, 22)
        game.direction = "l"
        old_head = game.snake[0]
        game.pellets = {}  # remove pellets to prevent eating
        game.tick()
        new_head = game.snake[0]
        assert new_head[0] == (old_head[0] + 1) % game.width
        assert new_head[1] == old_head[1]

    def test_wraps_horizontally(self):
        """Test that snake wraps around the right edge."""
        game = Snake(40, 22)
        game.direction = "l"
        # Place head at right edge
        game.snake = [(game.width - 1, 10), (game.width - 2, 10), (game.width - 3, 10)]
        game.pellets = {}
        game.tick()
        assert game.snake[0] == (0, 10)

    def test_wraps_vertically(self):
        """Test that snake wraps around the bottom edge."""
        game = Snake(40, 22)
        game.direction = "j"
        # Place head at bottom edge
        game.snake = [(10, game.height - 1), (10, game.height - 2), (10, game.height - 3)]
        game.pellets = {}
        game.tick()
        assert game.snake[0] == (10, 0)

    def test_does_not_tick_after_game_over(self):
        """Test that tick is a no-op when game is over."""
        game = Snake(40, 22)
        game._game_over = True
        old_head = game.snake[0]
        game.tick()
        assert game.snake[0] == old_head


class TestSnakeEating:
    """Tests for pellet eating mechanics."""

    def test_eating_pellet_increases_score(self):
        """Test that eating a pellet increments the score."""
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = {next_pos: PELLET_EMOJIS[0]}
        game.tick()
        assert game.score == 1

    def test_eating_pellet_grows_snake(self):
        """Test that eating a pellet triggers growth."""
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = {next_pos: PELLET_EMOJIS[0]}
        old_len = len(game.snake)
        game.tick()
        # Snake should start growing (grow_pending set)
        assert game._grow_pending == GROW_ON_EAT - 1  # one used this tick

    def test_eating_spawns_new_pellets(self):
        """Test that eating a pellet spawns replacement pellets."""
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = {next_pos: PELLET_EMOJIS[0]}
        game.tick()
        # Should have spawned 2 new pellets (old one eaten)
        assert len(game.pellets) == 2


class TestSnakeCollision:
    """Tests for self-collision."""

    def test_self_collision_game_over(self):
        """Test that colliding with own body triggers game over."""
        game = Snake(40, 22)
        # Create a snake that will run into itself
        # Snake going right, with body forming a loop
        game.snake = [
            (5, 5),   # head
            (5, 4),   # above
            (6, 4),   # right of above
            (6, 5),   # right of head
            (6, 6),   # below right
        ]
        game.direction = "l"  # moving right
        game.pellets = {}
        game.tick()  # head moves to (6, 5) which is occupied
        assert game.is_game_over() is True


class TestSnakeHandleInput:
    """Tests for Snake.handle_input."""

    def test_change_direction(self):
        """Test that valid direction input changes snake direction."""
        game = Snake(40, 22)
        game.direction = "l"  # right
        game.handle_input("j")  # down
        assert game.direction == "j"

    def test_cannot_reverse(self):
        """Test that snake cannot reverse into itself."""
        game = Snake(40, 22)
        game.direction = "l"  # right
        game.handle_input("h")  # left (opposite)
        assert game.direction == "l"  # unchanged

    def test_all_directions(self):
        """Test that all four directions can be set."""
        game = Snake(40, 22)
        for d in ["h", "j", "k", "l"]:
            game2 = Snake(40, 22)
            # Set to a direction that allows the change
            game2.direction = "j" if d in ["h", "l"] else "l"
            game2.handle_input(d)
            assert game2.direction == d

    def test_invalid_key_ignored(self):
        """Test that unrecognized keys do not change direction."""
        game = Snake(40, 22)
        game.direction = "l"
        game.handle_input("x")
        assert game.direction == "l"

    def test_wasd_keys(self):
        """Test that w/a/s/d map to k/h/j/l directions."""
        game = Snake(40, 22)
        game.direction = "l"  # moving right
        game.handle_input("w")  # up
        assert game.direction == "k"

        game.direction = "l"
        game.handle_input("s")  # down
        assert game.direction == "j"

        game.direction = "k"  # moving up
        game.handle_input("a")  # left
        assert game.direction == "h"

        game.direction = "k"
        game.handle_input("d")  # right
        assert game.direction == "l"

    def test_wasd_cannot_reverse(self):
        """Test that WASD keys also respect opposite-direction restriction."""
        game = Snake(40, 22)
        game.direction = "l"  # moving right
        game.handle_input("a")  # left (opposite)
        assert game.direction == "l"  # unchanged


class TestSnakeGetFrame:
    """Tests for Snake.get_frame method."""

    def test_frame_is_list_of_strings(self):
        """Test that frame returns a list of strings."""
        game = Snake(40, 22)
        frame = game.get_frame()
        assert isinstance(frame, list)
        assert all(isinstance(line, str) for line in frame)

    def test_frame_has_correct_grid_rows(self):
        """Test that frame has height + 2 lines for grid and status."""
        game = Snake(40, 22)
        frame = game.get_frame()
        # height grid rows + blank + status = height + 2
        assert len(frame) == game.height + 2

    def test_frame_shows_rabbit_head(self):
        """Test that the rabbit head emoji appears in the frame."""
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "\U0001f430" in grid_text

    def test_frame_shows_tail(self):
        """Test that the white tail emoji appears for all body segments."""
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert CELL_TAIL in grid_text
        # Body has 2 segments (length 3 minus head), so tail emoji appears twice
        assert grid_text.count(CELL_TAIL) == 2

    def test_frame_shows_pellets(self):
        """Test that a pellet emoji appears in the frame."""
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert any(e in grid_text for e in PELLET_EMOJIS)

    def test_frame_has_status_line(self):
        """Test that status line shows game name, score, and cancel."""
        game = Snake(40, 22)
        frame = game.get_frame()
        assert "Rabbit" in frame[-1]
        assert "Score" in frame[-1]
        assert "[c]" in frame[-1]


class TestSnakeSpawnPellets:
    """Tests for pellet spawning edge cases."""

    def test_no_spawn_when_grid_full(self):
        """Test that _spawn_pellets is a no-op when no cells are available."""
        game = Snake(20, 12)  # minimum size: 10x10 grid
        # Fill every cell with the snake body
        game.snake = [
            (x, y) for y in range(game.height) for x in range(game.width)
        ]
        game.pellets = {}
        game._spawn_pellets(5)
        assert len(game.pellets) == 0

    def test_pellets_are_random_emojis(self):
        """Test that spawned pellets use emojis from PELLET_EMOJIS."""
        game = Snake(40, 22)
        for emoji in game.pellets.values():
            assert emoji in PELLET_EMOJIS

    def test_pellets_stored_as_dict(self):
        """Test that pellets map positions to emoji strings."""
        game = Snake(40, 22)
        assert isinstance(game.pellets, dict)
        assert len(game.pellets) == INITIAL_PELLETS
        for pos, emoji in game.pellets.items():
            assert isinstance(pos, tuple)
            assert isinstance(emoji, str)


class TestSnakeGameOver:
    """Tests for Snake game over state."""

    def test_game_over_frame(self):
        """Test that game over frame shows score and GAME OVER text."""
        game = Snake(40, 22)
        game._game_over = True
        game.score = 5
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "GAME OVER" in full_text
        assert "5" in full_text
        assert "[c]" in full_text
