"""Tests for vim4rabbit.games.rabbit module."""

import pytest
from vim4rabbit.games.rabbit import (
    Snake, DIRECTIONS, WASD_MAP, INITIAL_PELLETS, GROW_ON_EAT,
    CELL_EMPTY, CELL_HEAD, CELL_TAIL, PELLET_EMOJIS,
    CELL_ENEMY_HEAD, CELL_ENEMY_TAIL, CELL_SKULL, ENEMY_LENGTH,
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

    def test_initial_pellets_is_20(self):
        """Test that INITIAL_PELLETS is 20."""
        assert INITIAL_PELLETS == 20

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

    def test_initial_enemy_snake(self):
        """Test that enemy snake is initialized with correct length."""
        game = Snake(40, 22)
        assert len(game.enemy) == ENEMY_LENGTH

    def test_enemy_length_is_13(self):
        """Test that ENEMY_LENGTH is 13."""
        assert ENEMY_LENGTH == 13

    def test_initial_enemy_direction(self):
        """Test that enemy starts moving left."""
        game = Snake(40, 22)
        assert game.enemy_direction == "h"

    def test_initial_skulls_empty(self):
        """Test that no skulls exist at start."""
        game = Snake(40, 22)
        assert len(game.skulls) == 0

    def test_initial_game_over_reason_empty(self):
        """Test that game over reason is empty at start."""
        game = Snake(40, 22)
        assert game._game_over_reason == ""


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
        # Move enemy away to prevent interference
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()
        assert len(game.snake) == initial_len

    def test_tick_moves_right(self):
        """Test that snake moves right when direction is 'l'."""
        game = Snake(40, 22)
        game.direction = "l"
        old_head = game.snake[0]
        game.pellets = {}
        # Move enemy away
        game.enemy = [(0, 0)] * ENEMY_LENGTH
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
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()
        assert game.snake[0] == (0, 10)

    def test_wraps_vertically(self):
        """Test that snake wraps around the bottom edge."""
        game = Snake(40, 22)
        game.direction = "j"
        # Place head at bottom edge
        game.snake = [(10, game.height - 1), (10, game.height - 2), (10, game.height - 3)]
        game.pellets = {}
        game.enemy = [(0, 0)] * ENEMY_LENGTH
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
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()
        assert game.score == 1

    def test_eating_pellet_grows_snake(self):
        """Test that eating a pellet triggers growth."""
        game = Snake(40, 22)
        game.direction = "l"
        head_x, head_y = game.snake[0]
        next_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = {next_pos: PELLET_EMOJIS[0]}
        game.enemy = [(0, 0)] * ENEMY_LENGTH
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
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()
        # Should have spawned 2 new pellets (old one eaten)
        assert len(game.pellets) == 2


class TestSnakeCollision:
    """Tests for self-collision."""

    def test_self_collision_game_over(self):
        """Test that colliding with own body triggers game over."""
        game = Snake(40, 22)
        # Create a snake that will run into itself
        game.snake = [
            (5, 5),   # head
            (5, 4),   # above
            (6, 4),   # right of above
            (6, 5),   # right of head
            (6, 6),   # below right
        ]
        game.direction = "l"  # moving right
        game.pellets = {}
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()  # head moves to (6, 5) which is occupied
        assert game.is_game_over() is True

    def test_self_collision_sets_reason(self):
        """Test that self-collision sets the reason."""
        game = Snake(40, 22)
        game.snake = [
            (5, 5), (5, 4), (6, 4), (6, 5), (6, 6),
        ]
        game.direction = "l"
        game.pellets = {}
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()
        assert game._game_over_reason == "Rabbit hit itself!"


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
        assert "Rabbit vs Snake" in frame[-1]
        assert "Score" in frame[-1]
        assert "[c]" in frame[-1]

    def test_frame_shows_enemy_head(self):
        """Test that the enemy snake head emoji appears in the frame."""
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert CELL_ENEMY_HEAD in grid_text

    def test_frame_shows_enemy_tail(self):
        """Test that the enemy snake tail emoji appears in the frame."""
        game = Snake(40, 22)
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert CELL_ENEMY_TAIL in grid_text
        # 12 tail segments (13 total minus head)
        assert grid_text.count(CELL_ENEMY_TAIL) == ENEMY_LENGTH - 1

    def test_frame_shows_skulls(self):
        """Test that skull emoji appears when skulls exist."""
        game = Snake(40, 22)
        game.skulls = {(1, 1)}
        frame = game.get_frame()
        grid_text = "".join(frame[:game.height])
        assert CELL_SKULL in grid_text


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

    def test_pellets_avoid_enemy(self):
        """Test that pellets don't spawn on enemy positions."""
        game = Snake(40, 22)
        enemy_positions = set(game.enemy)
        for pos in game.pellets:
            assert pos not in enemy_positions


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

    def test_game_over_frame_shows_reason(self):
        """Test that game over frame shows the reason."""
        game = Snake(40, 22)
        game._game_over = True
        game._game_over_reason = "Rabbit hit the snake!"
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "Rabbit hit the snake!" in full_text

    def test_game_over_frame_shows_game_name(self):
        """Test that game over frame shows Rabbit vs Snake."""
        game = Snake(40, 22)
        game._game_over = True
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "Rabbit vs Snake" in full_text

    def test_game_over_frame_shows_play_again(self):
        """Test that game over frame shows play again option."""
        game = Snake(40, 22)
        game._game_over = True
        frame = game.get_game_over_frame()
        full_text = "\n".join(frame)
        assert "[p] play again?" in full_text

    def test_play_again_resets_game(self):
        """Test that pressing p after game over resets the game."""
        game = Snake(40, 22)
        game._game_over = True
        game.score = 10
        game.handle_input("p")
        assert game.is_game_over() is False
        assert game.score == 0
        assert len(game.snake) == 3
        assert len(game.pellets) == INITIAL_PELLETS
        assert len(game.enemy) == ENEMY_LENGTH
        assert len(game.skulls) == 0

    def test_play_again_ignored_during_gameplay(self):
        """Test that p key does not reset during active gameplay."""
        game = Snake(40, 22)
        game.score = 5
        game.handle_input("p")
        assert game.score == 5  # unchanged


class TestEnemySnake:
    """Tests for enemy snake behavior."""

    def test_enemy_random_turn_from_vertical(self, monkeypatch):
        """Test that enemy turns from vertical to horizontal direction."""
        monkeypatch.setattr("random.random", lambda: 0.0)  # force turn
        monkeypatch.setattr("random.choice", lambda seq: seq[0])
        game = Snake(40, 22)
        game.enemy_direction = "j"  # moving down
        game.pellets = {}
        game._tick_enemy()
        assert game.enemy_direction in ("h", "l")

    def test_enemy_moves_on_tick(self):
        """Test that enemy snake moves each tick."""
        game = Snake(40, 22)
        game.pellets = {}
        game.enemy = [(15, 5)] + [(15 + i, 5) for i in range(1, ENEMY_LENGTH)]
        game.enemy_direction = "h"
        old_head = game.enemy[0]
        game._tick_enemy()
        assert game.enemy[0] != old_head

    def test_enemy_fixed_length(self):
        """Test that enemy snake maintains fixed length."""
        game = Snake(40, 22)
        game.pellets = {}
        for _ in range(10):
            game._tick_enemy()
        assert len(game.enemy) == ENEMY_LENGTH

    def test_enemy_eats_pellet_creates_skull(self, monkeypatch):
        """Test that enemy eating a pellet creates a skull."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turns
        game = Snake(40, 22)
        # Set up enemy to move left into a pellet
        game.enemy_direction = "h"
        head_x, head_y = game.enemy[0]
        pellet_pos = ((head_x - 1) % game.width, head_y)
        game.pellets = {pellet_pos: PELLET_EMOJIS[0]}
        game._tick_enemy()
        assert pellet_pos in game.skulls
        assert pellet_pos not in game.pellets

    def test_enemy_wraps_around(self, monkeypatch):
        """Test that enemy wraps around board edges."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turn
        game = Snake(40, 22)
        game.enemy_direction = "h"  # moving left
        game.enemy = [(0, 5)] + [(i, 5) for i in range(1, ENEMY_LENGTH)]
        game.pellets = {}
        game._tick_enemy()
        assert game.enemy[0] == (game.width - 1, 5)

    def test_enemy_can_cross_own_tail(self, monkeypatch):
        """Test that enemy snake is allowed to cross its own tail."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turn
        game = Snake(40, 22)
        game.enemy_direction = "l"  # moving right
        # Body segment at (6, 5) is in the path — enemy should cross it
        game.enemy = [
            (5, 5),   # head
            (4, 5),
            (4, 4),
            (5, 4),
            (6, 4),
            (6, 5),   # in the forward path
            (6, 6),
            (5, 6),
            (4, 6),
            (3, 6),
            (3, 5),
            (3, 4),
            (3, 3),
        ]
        game.pellets = {}
        game._tick_enemy()
        assert game.enemy[0] == (6, 5)
        assert len(game.enemy) == ENEMY_LENGTH


class TestRabbitVsSnakeCollisions:
    """Tests for rabbit-enemy interactions."""

    def test_rabbit_hits_enemy_body_game_over(self, monkeypatch):
        """Test that rabbit hitting enemy body triggers game over."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turn
        game = Snake(40, 22)
        game.direction = "l"  # rabbit moving right
        head_x, head_y = game.snake[0]
        # Place enemy body where rabbit will move; enemy moves away (up)
        enemy_pos = ((head_x + 1) % game.width, head_y)
        game.enemy = [enemy_pos] + [(enemy_pos[0], enemy_pos[1] + i)
                                     for i in range(1, ENEMY_LENGTH)]
        game.enemy_direction = "k"  # enemy moves up, away from rabbit
        game.pellets = {}
        game.skulls = set()
        game.tick()
        assert game.is_game_over() is True
        assert game._game_over_reason == "Rabbit hit the snake!"

    def test_rabbit_hits_enemy_head_game_over(self, monkeypatch):
        """Test that rabbit hitting enemy head triggers game over."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turn
        game = Snake(40, 22)
        game.direction = "l"  # rabbit moving right
        head_x, head_y = game.snake[0]
        # Place enemy 2 cells right; enemy moves right (away)
        enemy_head = ((head_x + 2) % game.width, head_y)
        game.enemy = [enemy_head] + [(enemy_head[0] + i, enemy_head[1])
                                      for i in range(1, ENEMY_LENGTH)]
        game.enemy_direction = "l"  # enemy moves right, away
        game.pellets = {}
        game.skulls = set()
        # After enemy moves right, enemy body still at (head_x+2, head_y)
        # Rabbit moves right to (head_x+1), then next tick to (head_x+2)
        game.tick()  # rabbit at head_x+1, enemy shifted right
        assert not game.is_game_over()
        game.tick()  # rabbit at head_x+2, enemy body still there
        assert game.is_game_over() is True

    def test_rabbit_eats_skull_game_over(self):
        """Test that rabbit eating a skull triggers game over."""
        game = Snake(40, 22)
        game.direction = "l"  # moving right
        head_x, head_y = game.snake[0]
        skull_pos = ((head_x + 1) % game.width, head_y)
        game.pellets = {}
        game.skulls = {skull_pos}
        game.enemy = [(0, 0)] * ENEMY_LENGTH
        game.tick()
        assert game.is_game_over() is True
        assert game._game_over_reason == "Rabbit ate a poisoned pellet!"

    def test_skull_stays_on_board(self):
        """Test that skulls are permanent (not removed by snake movement)."""
        game = Snake(40, 22)
        skull_pos = (3, 3)
        game.skulls = {skull_pos}
        game.pellets = {}
        game.enemy = [(15, 15)] + [(15 + i, 15) for i in range(1, ENEMY_LENGTH)]
        game.enemy_direction = "h"
        for _ in range(5):
            game._tick_enemy()
        assert skull_pos in game.skulls

    def test_multiple_skulls_accumulate(self, monkeypatch):
        """Test that multiple skulls can exist on the board."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turns
        game = Snake(40, 22)
        game.skulls = set()
        game.enemy_direction = "h"
        head_x, head_y = game.enemy[0]
        pos1 = ((head_x - 1) % game.width, head_y)
        pos2 = ((head_x - 2) % game.width, head_y)
        game.pellets = {
            pos1: PELLET_EMOJIS[0],
            pos2: PELLET_EMOJIS[1],
        }
        game._tick_enemy()
        game._tick_enemy()
        assert len(game.skulls) == 2

    def test_snake_hits_rabbit_game_over(self, monkeypatch):
        """Test that enemy snake hitting rabbit body triggers game over."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turn
        game = Snake(40, 22)
        game.enemy_direction = "h"  # moving left
        # Place rabbit body where enemy will move
        rabbit_pos = (game.enemy[0][0] - 1, game.enemy[0][1])
        game.snake = [rabbit_pos, (rabbit_pos[0], rabbit_pos[1] + 1),
                       (rabbit_pos[0], rabbit_pos[1] + 2)]
        game.pellets = {}
        game.skulls = set()
        game.tick()
        assert game.is_game_over() is True
        assert game._game_over_reason == "The snake caught the rabbit!"

    def test_snake_hits_rabbit_head_game_over(self, monkeypatch):
        """Test that enemy snake hitting rabbit head triggers game over."""
        monkeypatch.setattr("random.random", lambda: 1.0)  # no random turn
        game = Snake(40, 22)
        game.enemy_direction = "h"  # moving left
        head_x, head_y = game.enemy[0]
        rabbit_head = ((head_x - 1) % game.width, head_y)
        game.snake = [rabbit_head, (rabbit_head[0] - 1, rabbit_head[1]),
                       (rabbit_head[0] - 2, rabbit_head[1])]
        game.pellets = {}
        game.skulls = set()
        game.tick()
        assert game.is_game_over() is True
