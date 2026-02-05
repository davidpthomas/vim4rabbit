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
    format_loading_message,
    format_review_output,
    get_animation_frame,
    get_no_work_animation_frame,
    get_no_work_frame_count,
    is_no_files_error,
    render_help,
)
from .parser import parse_review_issues


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
    issues: list,
    error_message: str,
) -> List[str]:
    """
    Format review results for display.

    Called from VimScript after vim_run_review().

    Args:
        success: Whether review succeeded
        issues: List of issues (each issue is list of line strings)
        error_message: Error message if failed

    Returns:
        List of strings (lines) for the review buffer
    """
    from .types import ReviewIssue, ReviewResult

    result = ReviewResult(
        success=success,
        issues=[ReviewIssue(lines=issue) for issue in issues],
        error_message=error_message,
    )

    return format_review_output(result)


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


def vim_get_animation_frame(frame: int) -> List[str]:
    """
    Get a specific animation frame for the loading spinner.

    Called from VimScript: py3eval('vim4rabbit.vim_get_animation_frame(' . frame . ')')

    Args:
        frame: Frame number (0-23, wraps around)

    Returns:
        List of strings for the animation frame
    """
    return get_animation_frame(frame)


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


# =============================================================================
# Convenience function for backward compatibility
# =============================================================================


def get_message() -> str:
    """Return the iconic message (kept for backward compatibility)."""
    return "All your vim are belong to us."
