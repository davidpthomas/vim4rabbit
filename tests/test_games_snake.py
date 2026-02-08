"""Tests for vim4rabbit.games.snake module."""

import pytest
from vim4rabbit.games.snake import Snake, DIRECTIONS, INITIAL_PELLETS, GROW_ON_EAT


class TestSnakeInit:
    """Tests for Snake initialization."""

    def test_default_dimensions(self):
        game = Snake(40, 22)
        assert game.width == 40
        assert game.height == 20  # height - 2 for status

    def test_minimum_dimensions(self):
        game = Snake(5, 5)
        assert game.width == 15
        assert game.height == 10

    def test_initial_snake_length(self):
        game = Snake(40, 22)
        assert len(game.snake) == 3

    def test_initial_pellet_count(self):
        game = Snake(40, 22)
        assert len(game.pellets) == INITIAL_PELLETS

    def test_initial_direction(self):
        game = Snake(40, 22)
        assert game.direction == "l"  # moving right

    def test_initial_score(self):
        game = Snake(40, 22)
        assert game.score == 0

    def test_not_game_over_initially(self):
        game = Snake(40, 22)
        assert game.is_game_over() is False


class TestSnakeTick:
    """Tests for Snake.tick method."""

    def test_tick_moves_head(self):
        game = Snake(40, 22)
        old_head = game.snake[0]
        game.tick()
        new_head = game.snake[0]
        assert old_head != new_head

    def test_tick_maintains_length(self):
        game = Snake(40, 22)
        initial_len = len(game.snake)
        # Remove all pellets to prevent eating
        game.pellets = []
        game.tick()
        assert len(game.snake) == initial_len

    def test_tick_moves_right(self):
        game = Snake(40, 22)
        game.direction = "l"
        old_head = game.snake[0]
        game.pellets = []  # remove pellets to prevent eating
        game.tick()
        new_head = game.snake[0]
        assert new_head[0] == (old_head[0] + 1) % game.width
        assert new_head[1] == old_head[1]

    def test_wraps_horizontally(self):
        game = Snake(40, 22)
        game.direction = "l"
        # Place head at right edge
        game.snake = [(game.width - 1, 10), (game.width - 2, 10), (game.width - 3, 10)]
        game.pellets = []
        game.tick()
        assert game.snake[0] == (0, 10)

    def test_wraps_vertically(self):
        game = Snake(40, 22)
        game.direction = "j"
        # Place head at bottom edge
        game.snake = [(10, game.height - 1), (10, game.height - 2), (10, game.height - 3)]
        game.pellets = []
        game.tick()
        assert game.snake[0] == (10, 0)

    def test_does_not_tick_after_game_over(self):
        game = Snake(40, 22)
        game._game_over = True
        old_head = game.snake[0]
        game.tick()
        assert game.snake[0] == old_head


class TestSnakeEating:
    """Tests for pellet eating mechanics."""

    def test_eating_pellet_increases_score(self):
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = [next_pos]
        game.tick()
        assert game.score == 1

    def test_eating_pellet_grows_snake(self):
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = [next_pos]
        old_len = len(game.snake)
        game.tick()
        # Snake should start growing (grow_pending set)
        assert game._grow_pending == GROW_ON_EAT - 1  # one used this tick

    def test_eating_spawns_new_pellets(self):
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = [next_pos]
        game.tick()
        # Should have spawned 2 new pellets (old one eaten)
        assert len(game.pellets) == 2


class TestSnakeCollision:
    """Tests for self-collision."""

    def test_self_collision_game_over(self):
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
        game.pellets = []
        game.tick()  # head moves to (6, 5) which is occupied
        assert game.is_game_over() is True


class TestSnakeHandleInput:
    """Tests for Snake.handle_input."""

    def test_change_direction(self):
        game = Snake(40, 22)
        game.direction = "l"  # right
        game.handle_input("j")  # down
        assert game.direction == "j"

    def test_cannot_reverse(self):
        game = Snake(40, 22)
        game.direction = "l"  # right
        game.handle_input("h")  # left (opposite)
        assert game.direction == "l"  # unchanged

    def test_all_directions(self):
        game = Snake(40, 22)
        for d in ["h", "j", "k", "l"]:
            game2 = Snake(40, 22)
            # Set to a direction that allows the change
            game2.direction = "j" if d in ["h", "l"] else "l"
            game2.handle_input(d)
            assert game2.direction == d

    def test_invalid_key_ignored(self):
        game = Snake(40, 22)
        game.direction = "l"
        game.handle_input("x")
        assert game.direction == "l"


class TestSnakeGetFrame:
    """Tests for Snake.get_frame method."""

    def test_frame_is_list_of_strings(self):
        game = Snake(40, 22)
        frame = game.get_frame()
        assert isinstance(frame, list)
        assert all(isinstance(line, str) for line in frame)

    def test_frame_has_correct_grid_rows(self):
        game = Snake(40, 22)
        frame = game.get_frame()
        # height grid rows + blank + status = height + 2
        assert len(frame) == game.height + 2

    def test_frame_shows_snake_head(self):
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "@" in grid_text

    def test_frame_shows_snake_body(self):
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "#" in grid_text

    def test_frame_shows_pellets(self):
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert "*" in grid_text

    def test_frame_has_status_line(self):
        game = Snake(40, 22)
        frame = game.get_frame()
        assert "Snake" in frame[-1]
        assert "Score" in frame[-1]
        assert "[c]" in frame[-1]


class TestSnakeSpawnPellets:
    """Tests for pellet spawning edge cases."""

    def test_no_spawn_when_grid_full(self):
        """Test that _spawn_pellets is a no-op when no cells are available."""
        game = Snake(15, 12)  # minimum size: 15x10 grid
        # Fill every cell with the snake body
        game.snake = [
            (x, y) for y in range(game.height) for x in range(game.width)
        ]
        game.pellets = []
        game._spawn_pellets(5)
        assert game.pellets == []


class TestSnakeGameOver:
    """Tests for Snake game over state."""

    def test_game_over_frame(self):
        game = Snake(40, 22)
        game._game_over = True
        game.score = 5
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "GAME OVER" in full_text
        assert "5" in full_text
        assert "[c]" in full_text
