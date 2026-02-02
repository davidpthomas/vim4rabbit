"""
Buffer content formatting for vim4rabbit.

This module handles generating content for Vim buffers.
"""

from typing import List, Tuple

from .types import ReviewResult


# Help content configuration
HELP_COMMANDS: List[List[Tuple[str, str]]] = [
    # Column 1
    [("r", "Review")],
    # Column 2
    [],
    # Column 3
    [],
]


def render_help(width: int) -> List[str]:
    """
    Render the help screen content with 3-column layout.

    Ported from vim4rabbit#RenderHelp().

    Args:
        width: Window width in characters

    Returns:
        List of strings (lines) for the help buffer
    """
    col_width = (width - 4) // 3

    content: List[str] = []

    # Header line with emoji
    content.append("  \U0001F430 vim4rabbit Help")  # rabbit emoji
    content.append("")

    # Get columns
    col1 = HELP_COMMANDS[0] if len(HELP_COMMANDS) > 0 else []
    col2 = HELP_COMMANDS[1] if len(HELP_COMMANDS) > 1 else []
    col3 = HELP_COMMANDS[2] if len(HELP_COMMANDS) > 2 else []

    # Calculate max rows needed across all columns
    max_rows = max(len(col1), len(col2), len(col3), 1)

    # Build command rows (3 columns)
    for row in range(max_rows):
        line = "  "

        # Column 1
        if row < len(col1):
            key, desc = col1[row]
            cell = f"[{key}] {desc}"
        else:
            cell = ""
        line += cell + " " * (col_width - len(cell))

        # Column 2
        if row < len(col2):
            key, desc = col2[row]
            cell = f"[{key}] {desc}"
        else:
            cell = ""
        line += cell + " " * (col_width - len(cell))

        # Column 3
        if row < len(col3):
            key, desc = col3[row]
            cell = f"[{key}] {desc}"
        else:
            cell = ""
        line += cell

        content.append(line)

    # Bottom line with quit on the right
    quit_text = "[q] Quit"
    padding = width - len(quit_text) - 4
    content.append(" " * padding + quit_text + "  ")

    return content


def format_review_output(result: ReviewResult) -> List[str]:
    """
    Format review output for display in buffer.

    Ported from vim4rabbit#RunReview() (content building part).

    Args:
        result: ReviewResult from running CodeRabbit

    Returns:
        List of strings (lines) for the review buffer
    """
    content: List[str] = []

    # Header
    content.append("  \U0001F430 coderabbit")  # rabbit emoji
    content.append("")

    if not result.success:
        content.append("  \u26A0\uFE0F  Error running coderabbit:")  # warning emoji
        content.append("")
        for line in result.error_message.split("\n"):
            content.append(f"    {line}")
    else:
        if not result.issues:
            content.append("  \u2713 No issues found!")  # checkmark
        else:
            content.append(f"  Found {len(result.issues)} issue(s):")

            for i, issue in enumerate(result.issues, 1):
                content.append("")
                content.append("  " + "\u2550" * 40)  # double line
                content.append(f"  Issue #{i}")
                content.append("  " + "\u2500" * 40)  # single line
                for line in issue.lines:
                    content.append(f"    {line}")

    content.append("")
    content.append("  Press [q] to close")

    return content


def format_loading_message() -> List[str]:
    """
    Format the loading message for the review buffer.

    Returns:
        List of strings for the loading state
    """
    return [
        "  \U0001F430 coderabbit",  # rabbit emoji
        "",
        "  Running coderabbit...",
        "",
        "  Press [c] to cancel",
    ]


def format_cancelled_message() -> List[str]:
    """
    Format the cancelled message for the review buffer.

    Returns:
        List of strings for the cancelled state
    """
    return [
        "  \U0001F430 coderabbit",  # rabbit emoji
        "",
        "  \u2717 Review cancelled",  # X mark
        "",
        "  Press [q] to close",
    ]


def format_animated_loading_message(spinner_frame: str, elapsed_time: str) -> List[str]:
    """
    Format the animated loading message with spinner and elapsed time.

    Args:
        spinner_frame: Current spinner frame character (e.g., '|', '/', '-', '\\')
        elapsed_time: Elapsed time string (e.g., '0:05', '1:23')

    Returns:
        List of strings for the animated loading state
    """
    return [
        "  \U0001F430 coderabbit",  # rabbit emoji
        "",
        f"  {spinner_frame} Running coderabbit... ({elapsed_time})",
        "",
        "  Press [c] to cancel",
    ]
