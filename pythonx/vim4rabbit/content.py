"""
Buffer content formatting for vim4rabbit.

This module handles generating content for Vim buffers.
"""

from typing import List, Tuple

from .types import ReviewResult


# Animation frames for rabbit eating vegetables (24 frames total)
# Vegetables: carrot 🥕, cabbage 🥬, broccoli 🥦, bell pepper 🫑
ANIMATION_FRAMES: List[List[str]] = [
    # Frame 0: Full plate
    [
        r"    (\__/)",
        r"    (='.'=)    🥕🥬🥦🫑",
        r'    (")_(")',
    ],
    # Frame 1: Excited to eat
    [
        r"    (\__/)",
        r"    (=°o°=)   🥕🥬🥦🫑  *crunch*",
        r'    (")_(")',
    ],
    # Frame 2: Chewing
    [
        r"    (\__/)",
        r"    (=^.^=)    🥕🥬🥦",
        r'    (")_(")',
    ],
    # Frame 3: More munching
    [
        r"    (\__/)",
        r"    (=°o°=)   🥕🥬🥦  *munch*",
        r'    (")_(")',
    ],
    # Frame 4: Happy chewing
    [
        r"    (\__/)",
        r"    (=~.~=)    🥕🥬🥦",
        r'    (")_(")',
    ],
    # Frame 5: Another bite
    [
        r"    (\__/)",
        r"    (=°o°=)   🥕🥬  *chomp*",
        r'    (")_(")',
    ],
    # Frame 6: Enjoying
    [
        r"    (\__/)",
        r"    (=^.^=)    🥕🥬🫑",
        r'    (")_(")',
    ],
    # Frame 7: Crunch
    [
        r"    (\__/)",
        r"    (=°o°=)   🥕🥬🫑  *crunch*",
        r'    (")_(")',
    ],
    # Frame 8: Satisfied
    [
        r"    (\__/)",
        r"    (=~.~=)    🥕🥬",
        r'    (")_(")',
    ],
    # Frame 9: More food
    [
        r"    (\__/)",
        r"    (='.'=)    🥦🫑🥕",
        r'    (")_(")',
    ],
    # Frame 10: Big bite
    [
        r"    (\__/)",
        r"    (=°o°=)   🥦🫑🥕  *munch*",
        r'    (")_(")',
    ],
    # Frame 11: Chewing happily
    [
        r"    (\__/)",
        r"    (=^.^=)    🥦🫑",
        r'    (")_(")',
    ],
    # Frame 12: Yum
    [
        r"    (\__/)",
        r"    (=~.~=)    🥬🥦🫑🥕",
        r'    (")_(")',
    ],
    # Frame 13: Chomp
    [
        r"    (\__/)",
        r"    (=°o°=)   🥬🥦🫑  *chomp*",
        r'    (")_(")',
    ],
    # Frame 14: Happy
    [
        r"    (\__/)",
        r"    (=^.^=)    🥬🥦",
        r'    (")_(")',
    ],
    # Frame 15: Munching
    [
        r"    (\__/)",
        r"    (=°o°=)   🥬🥦  *crunch*",
        r'    (")_(")',
    ],
    # Frame 16: Content
    [
        r"    (\__/)",
        r"    (=~.~=)    🥕🫑",
        r'    (")_(")',
    ],
    # Frame 17: Another bite
    [
        r"    (\__/)",
        r"    (=°o°=)   🥕🫑  *munch*",
        r'    (")_(")',
    ],
    # Frame 18: Almost done
    [
        r"    (\__/)",
        r"    (=^.^=)    🥕🥬🥦",
        r'    (")_(")',
    ],
    # Frame 19: Chomp
    [
        r"    (\__/)",
        r"    (=°o°=)   🥬🥦  *chomp*",
        r'    (")_(")',
    ],
    # Frame 20: Few left
    [
        r"    (\__/)",
        r"    (=^.^=)    🥕🫑",
        r'    (")_(")',
    ],
    # Frame 21: Last bites
    [
        r"    (\__/)",
        r"    (=°o°=)   🥕  *crunch*",
        r'    (")_(")',
    ],
    # Frame 22: One more
    [
        r"    (\__/)",
        r"    (=^.^=)    🫑",
        r'    (")_(")',
    ],
    # Frame 23: All done - satisfied!
    [
        r"    (\__/)",
        r"    (=~.~=)      *yum!*",
        r'    (")_(")',
    ],
]


def get_animation_frame(frame_number: int) -> List[str]:
    """
    Get a complete animation frame for the loading state.

    Args:
        frame_number: The frame index (0-23, wraps around)

    Returns:
        List of strings for the complete frame including header and footer
    """
    frame_index = frame_number % len(ANIMATION_FRAMES)
    rabbit_lines = ANIMATION_FRAMES[frame_index]

    content: List[str] = [
        "  \U0001F430 coderabbit",  # rabbit emoji header
        "",
        "  Coderabbit review in progress!",
        "",
        "  This may take 30-90+ sec depending on the size of the review.",
        "  Your results will be displayed shortly...",
        "",
    ]
    content.extend(rabbit_lines)
    content.append("")
    content.append("  Press [c] to cancel")

    return content


# Help content configuration
HELP_COMMANDS: List[List[Tuple[str, str]]] = [
    # Column 1
    [("ru", "Review Uncommitted"), ("rc", "Review Committed"), ("ra", "Review All")],
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


# Animation frames for rabbit looking for work (8 frames total)
# Features a jumping rabbit with a large speech bubble
NO_WORK_ANIMATION_FRAMES: List[List[str]] = [
    # Frame 0: Rabbit on ground, looking around
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"                    ╱",
        r"                   ╱",
        r"              (\__/) ",
        r"              (='.'=)   ?",
        r"              (\")_(\")",
        r"         ════════════════",
    ],
    # Frame 1: Rabbit starts jumping
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"                    ╱",
        r"              (\__/)",
        r"              (=°o°=)  !",
        r"              (\")_(\")",
        r"                 ↑",
        r"         ════════════════",
    ],
    # Frame 2: Rabbit mid-air (low)
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"              (\__/)  ╱",
        r"              (=^.^=)",
        r"              (\")_(\")",
        r"",
        r"",
        r"         ════════════════",
    ],
    # Frame 3: Rabbit at peak
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰───────────(\__/)────────────────╯",
        r"                   (=°o°=)",
        r"                   (\")_(\")",
        r"",
        r"",
        r"",
        r"         ════════════════",
    ],
    # Frame 4: Rabbit descending
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"              (\__/)  ╲",
        r"              (=^.^=)",
        r"              (\")_(\")",
        r"                 ↓",
        r"",
        r"         ════════════════",
    ],
    # Frame 5: Rabbit landing
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"                    ╲",
        r"              (\__/)",
        r"              (=~.~=) *boing*",
        r"              (\")_(\")",
        r"",
        r"         ════════════════",
    ],
    # Frame 6: Rabbit bounced, looking left
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"                    ╱",
        r"                   ╱",
        r"         ?    (\__/)",
        r"              (='.'=)",
        r"              (\")_(\")",
        r"         ════════════════",
    ],
    # Frame 7: Rabbit looking right
    [
        r"       ╭─────────────────────────────────╮",
        r"       │                                 │",
        r"       │   No changes to review!         │",
        r"       │   Looking for work...           │",
        r"       │                                 │",
        r"       ╰─────────────────────────────────╯",
        r"                    ╱",
        r"                   ╱",
        r"              (\__/)    ?",
        r"              (='.'=)",
        r"              (\")_(\")",
        r"         ════════════════",
    ],
]


def get_no_work_animation_frame(frame_number: int) -> List[str]:
    """
    Get a complete animation frame for the "no work" state.

    Shows a rabbit jumping up and down looking for work.

    Args:
        frame_number: The frame index (0-7, wraps around)

    Returns:
        List of strings for the complete frame including header and footer
    """
    frame_index = frame_number % len(NO_WORK_ANIMATION_FRAMES)
    rabbit_lines = NO_WORK_ANIMATION_FRAMES[frame_index]

    content: List[str] = [
        "  \U0001F430 coderabbit",  # rabbit emoji header
        "",
    ]
    content.extend(rabbit_lines)
    content.append("")
    content.append("  Press [q] to close")

    return content


def get_no_work_frame_count() -> int:
    """Return the number of frames in the no-work animation."""
    return len(NO_WORK_ANIMATION_FRAMES)


def is_no_files_error(error_message: str) -> bool:
    """
    Check if the error message indicates no files to review.

    Args:
        error_message: The error message from CodeRabbit

    Returns:
        True if this is a "no files" error, False otherwise
    """
    if not error_message:
        return False

    error_lower = error_message.lower()
    no_files_indicators = [
        "no files",
        "no changes",
        "nothing to review",
        "no diff",
        "failed to start review",
    ]
    return any(indicator in error_lower for indicator in no_files_indicators)
