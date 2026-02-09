"""
vim4rabbit - A Vim plugin powered by Python

This module provides the Python backend for vim4rabbit.
All vim_* functions are the public API called from VimScript via py3eval().
"""

__version__ = "0.1.0"

from typing import List

from .cli import run_review
from .content import (
    format_cancelled_message,
    format_elapsed_time,
    format_loading_message,
    format_review_output,
    get_animation_frame,
    get_no_work_animation_frame,
    get_no_work_frame_count,
    is_no_files_error,
    render_help,
)
from .games import (
    get_game_match_patterns,
    get_game_menu,
    get_tick_rate,
    input_game,
    is_game_active,
    start_game,
    stop_game,
    tick_game,
)
from .parser import parse_review_issues
from . import selection


# =============================================================================
# Public API for VimScript (vim_* functions)
# =============================================================================


def vim_run_review() -> dict:
    """
    Run CodeRabbit review and return results.

    Called from VimScript: py3eval('vim4rabbit.vim_run_review()')

    Returns:
        Dict with keys:
        - success: bool
        - issues: list of lists (each issue is a list of line strings)
        - error_message: str (empty if success)
    """
    result = run_review()
    return result.to_dict()


def vim_render_help(width: int) -> List[str]:
    """
    Render help content for the given window width.

    Called from VimScript: py3eval('vim4rabbit.vim_render_help(' . winwidth(0) . ')')

    Args:
        width: Window width in characters

    Returns:
        List of strings (lines) for the help buffer
    """
    return render_help(width)


def vim_format_review(
    success: bool,
    issues_data: list,
    error_message: str,
    elapsed_secs: int = 0,
) -> dict:
    """
    Format review results for display.

    Called from VimScript after vim_parse_review_output().

    Args:
        success: Whether review succeeded
        issues_data: List of issue dicts with full metadata (from issues_data),
                     or list of line-lists for backward compatibility
        error_message: Error message if failed
        elapsed_secs: Total elapsed seconds for the review command

    Returns:
        Dict with keys:
        - lines: List of strings for the review buffer
        - issue_count: Number of issues found
    """
    from .types import ReviewIssue, ReviewResult

    review_issues = []
    for item in issues_data:
        if isinstance(item, dict):
            review_issues.append(ReviewIssue(
                lines=item.get("lines", []),
                file_path=item.get("file_path", ""),
                line_range=item.get("line_range", ""),
                issue_type=item.get("issue_type", ""),
                summary=item.get("summary", ""),
                prompt=item.get("prompt", ""),
            ))
        else:
            # Backward compatibility: plain list of lines
            review_issues.append(ReviewIssue(lines=item))

    result = ReviewResult(
        success=success,
        issues=review_issues,
        error_message=error_message,
    )

    return format_review_output(result, elapsed_secs=elapsed_secs)


def vim_get_loading_content() -> List[str]:
    """
    Get the loading message content.

    Called from VimScript: py3eval('vim4rabbit.vim_get_loading_content()')

    Returns:
        List of strings for loading state
    """
    return format_loading_message()


def vim_get_cancelled_content() -> List[str]:
    """
    Get the cancelled message content.

    Called from VimScript: py3eval('vim4rabbit.vim_get_cancelled_content()')

    Returns:
        List of strings for cancelled state
    """
    return format_cancelled_message()


def vim_get_animation_frame(frame: int, elapsed_secs: int = 0) -> List[str]:
    """
    Get a specific animation frame for the loading spinner.

    Called from VimScript: py3eval('vim4rabbit.vim_get_animation_frame(frame, secs)')

    Args:
        frame: Frame number (0-23, wraps around)
        elapsed_secs: Elapsed seconds since review started

    Returns:
        List of strings for the animation frame
    """
    return get_animation_frame(frame, elapsed_secs=elapsed_secs)


def vim_get_no_work_animation_frame(frame: int) -> List[str]:
    """
    Get a specific animation frame for the "no work" state.

    Called from VimScript: py3eval('vim4rabbit.vim_get_no_work_animation_frame(' . frame . ')')

    Args:
        frame: Frame number (0-7, wraps around)

    Returns:
        List of strings for the animation frame
    """
    return get_no_work_animation_frame(frame)


def vim_get_no_work_frame_count() -> int:
    """
    Get the number of frames in the no-work animation.

    Called from VimScript: py3eval('vim4rabbit.vim_get_no_work_frame_count()')

    Returns:
        Number of frames (8)
    """
    return get_no_work_frame_count()


def vim_is_no_files_error(error_message: str) -> bool:
    """
    Check if an error message indicates no files to review.

    Called from VimScript: py3eval('vim4rabbit.vim_is_no_files_error(' . string(msg) . ')')

    Args:
        error_message: The error message to check

    Returns:
        True if this is a "no files" error
    """
    return is_no_files_error(error_message)


def vim_parse_review_output(output: str) -> dict:
    """
    Parse raw review output from async job.

    Called from VimScript after async job completes.

    Args:
        output: Raw output from coderabbit CLI

    Returns:
        Dict with keys:
        - success: bool
        - issues: list of lists (each issue is a list of line strings)
        - issues_data: list of dicts with full issue metadata
        - error_message: str (empty if success)
    """
    from .types import ReviewResult

    issues = parse_review_issues(output)
    result = ReviewResult(
        success=True,
        issues=issues,
        raw_output=output,
    )
    return result.to_dict()


def vim_build_claude_prompt(selected_indices: List[int], issues_data: List[dict]) -> str:
    """
    Build a combined prompt for Claude from selected issues.

    Called from VimScript: py3eval('vim4rabbit.vim_build_claude_prompt(...)')

    Args:
        selected_indices: List of 1-based issue numbers that are selected
        issues_data: List of issue dicts with full metadata (from issues_data)

    Returns:
        Combined prompt string for Claude CLI
    """
    if not selected_indices or not issues_data:
        return ""

    prompts: List[str] = []

    for idx in selected_indices:
        # Convert 1-based index to 0-based
        issue_idx = idx - 1
        if 0 <= issue_idx < len(issues_data):
            issue = issues_data[issue_idx]
            prompt = issue.get("prompt", "")
            file_path = issue.get("file_path", "")
            line_range = issue.get("line_range", "")
            summary = issue.get("summary", "")

            if prompt:
                # Use the AI prompt from CodeRabbit
                prompts.append(prompt)
            elif file_path:
                # Fallback: build a prompt from metadata
                location = file_path
                if line_range:
                    location += f":{line_range}"
                prompts.append(f"Fix the issue in {location}: {summary}")

    if not prompts:
        return ""

    # Combine prompts with clear separation
    if len(prompts) == 1:
        return prompts[0]

    combined = "Please address the following code review issues:\n\n"
    for i, prompt in enumerate(prompts, 1):
        combined += f"## Issue {i}\n{prompt}\n\n"

    return combined.strip()


# =============================================================================
# Selection API for VimScript (vim_* functions)
# =============================================================================


def vim_init_selections(issue_count: int) -> None:
    """
    Initialize selection state for a new review.

    Called from VimScript: py3eval('vim4rabbit.vim_init_selections(count)')
    """
    selection.init_selections(issue_count)


def vim_reset_selections() -> None:
    """
    Clear all selection state (on cleanup).

    Called from VimScript: py3eval('vim4rabbit.vim_reset_selections()')
    """
    selection.reset_selections()


def vim_toggle_selection(issue_num: int) -> bool:
    """
    Toggle selection for an issue number.

    Called from VimScript: py3eval('vim4rabbit.vim_toggle_selection(num)')

    Returns:
        New selection state (True = selected)
    """
    return selection.toggle_selection(issue_num)


def vim_select_all() -> int:
    """
    Select all issues.

    Called from VimScript: py3eval('vim4rabbit.vim_select_all()')

    Returns:
        Number of issues selected
    """
    return selection.select_all()


def vim_deselect_all() -> int:
    """
    Deselect all issues.

    Called from VimScript: py3eval('vim4rabbit.vim_deselect_all()')

    Returns:
        Number of issues deselected
    """
    return selection.deselect_all()


def vim_get_selected() -> List[int]:
    """
    Get sorted list of selected issue numbers.

    Called from VimScript: py3eval('vim4rabbit.vim_get_selected()')

    Returns:
        Sorted list of 1-based issue numbers
    """
    return selection.get_selected()


def vim_get_issue_count() -> int:
    """
    Get total number of issues.

    Called from VimScript: py3eval('vim4rabbit.vim_get_issue_count()')

    Returns:
        Total issue count
    """
    return selection.get_issue_count()


def vim_find_issue_at_line(lines: List[str], cursor_line_index: int) -> int:
    """
    Find issue number at the given cursor line.

    Called from VimScript: py3eval('vim4rabbit.vim_find_issue_at_line(lines, idx)')

    Args:
        lines: Buffer lines (0-indexed list)
        cursor_line_index: 0-based line index of cursor

    Returns:
        Issue number (1-based) or 0 if not found
    """
    return selection.find_issue_at_line(lines, cursor_line_index)


# =============================================================================
# Convenience function for backward compatibility
# =============================================================================


def get_message() -> str:
    """Return the iconic message (kept for backward compatibility)."""
    return "All your vim are belong to us."


# =============================================================================
# Game API for VimScript (vim_* functions)
# =============================================================================


def vim_get_game_menu(width: int = 80, height: int = 24) -> List[str]:
    """
    Get the game selection menu, centered in the given dimensions.

    Called from VimScript: py3eval('vim4rabbit.vim_get_game_menu(w, h)')
    """
    return get_game_menu(width, height)


def vim_start_game(key: str, width: int, height: int) -> int:
    """
    Start a game by key. Returns tick rate in ms, or 0 if invalid key.

    Called from VimScript: py3eval('vim4rabbit.vim_start_game(key, w, h)')
    """
    if start_game(key, width, height):
        return get_tick_rate(key)
    return 0


def vim_stop_game() -> None:
    """
    Stop the active game.

    Called from VimScript: py3eval('vim4rabbit.vim_stop_game()')
    """
    stop_game()


def vim_is_game_active() -> bool:
    """
    Check if a game is active.

    Called from VimScript: py3eval('vim4rabbit.vim_is_game_active()')
    """
    return is_game_active()


def vim_tick_game() -> List[str]:
    """
    Advance game one tick and return frame.

    Called from VimScript: py3eval('vim4rabbit.vim_tick_game()')
    """
    return tick_game()


def vim_input_game(key: str) -> List[str]:
    """
    Handle game input and return frame.

    Called from VimScript: py3eval('vim4rabbit.vim_input_game(key)')
    """
    return input_game(key)


def vim_get_game_match_patterns() -> List[List[str]]:
    """
    Get highlight match patterns from the active game.

    Called from VimScript: py3eval('vim4rabbit.vim_get_game_match_patterns()')

    Returns:
        List of [highlight_group, vim_regex_pattern] pairs, or empty list.
    """
    return get_game_match_patterns()
