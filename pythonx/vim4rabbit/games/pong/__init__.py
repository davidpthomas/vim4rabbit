"""
Pong game - Classic pong with j/k controls (V4R-51).

Human plays left paddle, AI plays right paddle.
Ball '*', paddles '|', center net ':'.
Game ends when a player reaches the winning score.
"""

import random
from typing import List, Tuple


WINNING_SCORE = 5
PADDLE_HEIGHT = 5
AI_SPEED = 1  # max cells AI paddle moves per tick


class Pong:
    """Classic pong game with human vs AI."""

    def __init__(self, width: int, height: int) -> None:
        self.width = max(width, 30)
        # Reserve 6 lines at bottom for scoreboard + status
        self.height = max(height - 6, 12)
        self.left_score = 0
        self.right_score = 0
        self._game_over = False
        self._winner = ""  # "left" or "right"

        # Paddles: y position is top of paddle
        self.paddle_h = min(PADDLE_HEIGHT, self.height // 3)
        self.left_y = (self.height - self.paddle_h) // 2
        self.right_y = (self.height - self.paddle_h) // 2

        # Paddle x positions
        self.left_x = 1
        self.right_x = self.width - 2

        # Ball
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = random.choice([-1, 1])
        self.ball_dy = random.choice([-1, 0, 1])

        # Serve delay: ticks to wait before ball moves after a point
        self._serve_delay = 3

    def _reset_ball(self, direction: int) -> None:
        """Reset ball to center, serving toward the given direction."""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = direction
        self.ball_dy = random.choice([-1, 0, 1])
        self._serve_delay = 3

    def _move_ai(self) -> None:
        """Move the AI paddle to track the ball."""
        paddle_center = self.right_y + self.paddle_h // 2
        if self.ball_dy == 0 and self.ball_dx < 0:
            # Ball moving away — drift toward center
            target = self.height // 2
        else:
            target = self.ball_y

        if paddle_center < target:
            self.right_y = min(self.right_y + AI_SPEED,
                               self.height - self.paddle_h)
        elif paddle_center > target:
            self.right_y = max(self.right_y - AI_SPEED, 0)

    def tick(self) -> None:
        """Advance game one step."""
        if self._game_over:
            return

        # Serve delay
        if self._serve_delay > 0:
            self._serve_delay -= 1
            self._move_ai()
            return

        # Move ball
        new_x = self.ball_x + self.ball_dx
        new_y = self.ball_y + self.ball_dy

        # Bounce off top/bottom walls
        if new_y < 0:
            new_y = -new_y
            self.ball_dy = -self.ball_dy
        elif new_y >= self.height:
            new_y = 2 * (self.height - 1) - new_y
            self.ball_dy = -self.ball_dy

        # Check left paddle hit
        if new_x <= self.left_x:
            if self.left_y <= new_y < self.left_y + self.paddle_h:
                new_x = self.left_x + 1
                self.ball_dx = 1
                # Vary dy based on hit position
                hit_pos = new_y - self.left_y
                self.ball_dy = self._deflect(hit_pos)
            else:
                # Right player scores
                self.right_score += 1
                if self.right_score >= WINNING_SCORE:
                    self._game_over = True
                    self._winner = "right"
                    return
                self._reset_ball(1)  # serve toward left player
                self._move_ai()
                return

        # Check right paddle hit
        if new_x >= self.right_x:
            if self.right_y <= new_y < self.right_y + self.paddle_h:
                new_x = self.right_x - 1
                self.ball_dx = -1
                hit_pos = new_y - self.right_y
                self.ball_dy = self._deflect(hit_pos)
            else:
                # Left player scores
                self.left_score += 1
                if self.left_score >= WINNING_SCORE:
                    self._game_over = True
                    self._winner = "left"
                    return
                self._reset_ball(-1)  # serve toward right player
                self._move_ai()
                return

        self.ball_x = new_x
        self.ball_y = new_y

        # Clamp ball within bounds
        self.ball_y = max(0, min(self.ball_y, self.height - 1))

        # Move AI paddle
        self._move_ai()

    def _deflect(self, hit_pos: int) -> int:
        """Calculate ball dy based on where it hit the paddle."""
        mid = self.paddle_h // 2
        if hit_pos < mid:
            return -1
        elif hit_pos > mid:
            return 1
        else:
            return 0

    def handle_input(self, key: str) -> None:
        """Handle paddle input (j=down, k=up)."""
        if key == "j":
            self.left_y = min(self.left_y + 1, self.height - self.paddle_h)
        elif key == "k":
            self.left_y = max(self.left_y - 1, 0)

    def get_frame(self) -> List[str]:
        """Render current game state."""
        grid = [[" "] * self.width for _ in range(self.height)]

        # Draw center net
        center_x = self.width // 2
        for y in range(self.height):
            if y % 2 == 0:
                grid[y][center_x] = ":"

        # Draw left paddle
        for i in range(self.paddle_h):
            py = self.left_y + i
            if 0 <= py < self.height:
                grid[py][self.left_x] = "|"

        # Draw right paddle
        for i in range(self.paddle_h):
            py = self.right_y + i
            if 0 <= py < self.height:
                grid[py][self.right_x] = "|"

        # Draw ball
        if 0 <= self.ball_y < self.height and 0 <= self.ball_x < self.width:
            grid[self.ball_y][self.ball_x] = "*"

        lines = ["".join(row) for row in grid]

        # Scoreboard (4 rows)
        lines.append("")
        lines.append(self._render_score_line())
        lines.append(self._render_score_bar())
        lines.append(
            f"  Pong  |  j/k to move  |  First to {WINNING_SCORE}  |  [c] cancel"
        )

        return lines

    def _render_score_line(self) -> str:
        """Render the score display line."""
        center = self.width // 2
        left_label = f"YOU: {self.left_score}"
        right_label = f"AI: {self.right_score}"
        # Pad to center around the midpoint
        left_part = left_label.rjust(center - 2)
        right_part = right_label.ljust(center - 2)
        return left_part + "    " + right_part

    def _render_score_bar(self) -> str:
        """Render a visual score bar."""
        left_dots = "*" * self.left_score + "." * (WINNING_SCORE - self.left_score)
        right_dots = "*" * self.right_score + "." * (WINNING_SCORE - self.right_score)
        center = self.width // 2
        left_part = f"  [{left_dots}]".ljust(center)
        right_part = f"[{right_dots}]"
        return left_part + right_part

    def is_game_over(self) -> bool:
        """Check if someone won."""
        return self._game_over

    def get_game_over_frame(self) -> List[str]:
        """Show winner celebration screen."""
        lines: List[str] = []
        lines.append("")
        lines.append("")
        cy = self.height // 2 - 5
        for _ in range(max(cy, 0)):
            lines.append("")

        if self._winner == "left":
            lines.append("        ╔═══════════════════════════════╗")
            lines.append("        ║                               ║")
            lines.append("        ║     YOU WIN!                  ║")
            lines.append(f"        ║     Score: {self.left_score} - {self.right_score}                 ║")
            lines.append("        ║                               ║")
            lines.append("        ║     Great game, champion!     ║")
            lines.append("        ╚═══════════════════════════════╝")
        else:
            lines.append("        ╔═══════════════════════════════╗")
            lines.append("        ║                               ║")
            lines.append("        ║     AI WINS!                  ║")
            lines.append(f"        ║     Score: {self.left_score} - {self.right_score}                 ║")
            lines.append("        ║                               ║")
            lines.append("        ║     Better luck next time!    ║")
            lines.append("        ╚═══════════════════════════════╝")

        lines.append("")
        lines.append("  Pong  |  [c] cancel")

        return lines
