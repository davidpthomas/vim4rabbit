"""
Buffer content formatting for vim4rabbit.

This module handles generating content for Vim buffers.
"""

from typing import List, Tuple

from .types import ReviewResult


def format_elapsed_time(seconds: int) -> str:
    """
    Format elapsed seconds as 'XXmin YYsec'.

    Args:
        seconds: Total elapsed seconds

    Returns:
        Formatted string like '03min 41sec'
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}min {secs:02d}sec"


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


def get_animation_frame(frame_number: int, elapsed_secs: int = 0) -> List[str]:
    """
    Get a complete animation frame for the loading state.

    Args:
        frame_number: The frame index (0-23, wraps around)
        elapsed_secs: Elapsed seconds since review started

    Returns:
        List of strings for the complete frame including header and footer
    """
    frame_index = frame_number % len(ANIMATION_FRAMES)
    rabbit_lines = ANIMATION_FRAMES[frame_index]

    elapsed_str = format_elapsed_time(elapsed_secs)

    content: List[str] = [
        "  \U0001F430 coderabbit",  # rabbit emoji header
        "",
        f"  Review in progress!  \U0001F552 {elapsed_str}",
        "",
        "  This may take a few minutes depending on the size of the review.",
        "  Your results will be displayed shortly...",
        "",
    ]
    content.extend(rabbit_lines)
    content.append("")
    content.append("  [p] play a game?  |  [c] cancel")

    return content


# Help content configuration
HELP_COMMANDS: List[List[Tuple[str, str]]] = [
    # Column 1
    [("u", "Review Uncommitted"), ("c", "Review Committed"), ("a", "Review All")],
]


def render_help(width: int) -> List[str]:
    """
    Render the help screen content with single column layout.

    Ported from vim4rabbit#RenderHelp().

    Args:
        width: Window width in characters

    Returns:
        List of strings (lines) for the help buffer
    """
    content: List[str] = []

    # Header line with emoji
    content.append("  \U0001F430 vim4rabbit Help")  # rabbit emoji
    content.append("")

    # Get commands
    commands = HELP_COMMANDS[0] if len(HELP_COMMANDS) > 0 else []

    # Build command rows
    for key, desc in commands:
        content.append(f"  [{key}] {desc}")

    # Bottom line with quit on the right
    quit_text = "[q] Close"
    padding = width - len(quit_text) - 4
    content.append(" " * padding + quit_text + "  ")

    return content


def format_review_output(result: ReviewResult, elapsed_secs: int = 0) -> dict:
    """
    Format review output for display in buffer with vim folds and checkboxes.

    Ported from vim4rabbit#RunReview() (content building part).
    Now includes:
    - Vim fold markers ({{{ and }}})
    - Checkbox prefixes [ ] for issue selection
    - Filtered preamble (content before first issue)
    - Elapsed time display

    Args:
        result: ReviewResult from running CodeRabbit
        elapsed_secs: Total elapsed seconds for the review command

    Returns:
        Dict with keys:
        - lines: List of strings for the review buffer
        - issue_count: Number of issues found
    """
    content: List[str] = []
    issue_count = 0

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
            issue_count = len(result.issues)
            elapsed_str = format_elapsed_time(elapsed_secs)
            content.append(
                f"  Found {issue_count} issue(s):  [\U0001F552 {elapsed_str}]"
            )
            content.append("")
            content.append("  Select an issue with [Space] then press @ to implement with Claude Code")
            content.append("")

            for i, issue in enumerate(result.issues, 1):
                # Build fold header with checkbox, number, type, summary, and location
                summary = issue.summary or "Issue"
                issue_type = issue.issue_type or "issue"
                location = ""
                if issue.file_path:
                    location = issue.file_path
                    if issue.line_range:
                        location += f":{issue.line_range}"
                    location = f" ({location})"

                # Fold header line with opening marker
                fold_header = (
                    f"  [ ] {i}. [{issue_type}] {summary}{location} "
                    + "{{" + "{"
                )
                content.append(fold_header)

                # Issue content (indented)
                for line in issue.lines:
                    content.append(f"    {line}")

                # Fold closing marker
                content.append("  " + "}}" + "}")
                content.append("")

    # Footer with keybinding hints
    content.append("  [za] toggle fold | [Space] toggle select | [@] claude | [c] close")

    return {"lines": content, "issue_count": issue_count}


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
        "  [p] play a game?  |  [c] cancel",
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
        "  Press [c] to close",
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
    content.append("  Press [c] to close")

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
