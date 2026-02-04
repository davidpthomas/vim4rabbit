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
        issues: List of issue dicts with keys: lines, location, summary
        error_message: Error message if failed

    Returns:
        List of strings (lines) for the review buffer
    """
    from .types import FileLocation, ReviewIssue, ReviewResult

    parsed_issues = []
    for issue in issues:
        if isinstance(issue, dict):
            location = None
            if issue.get("location"):
                loc = issue["location"]
                location = FileLocation(
                    filepath=loc["filepath"],
                    line=loc.get("line"),
                )
            parsed_issues.append(ReviewIssue(
                lines=issue.get("lines", []),
                location=location,
                summary=issue.get("summary", ""),
            ))
        else:
            # Backward compatibility: plain list of lines
            parsed_issues.append(ReviewIssue(lines=issue))

    result = ReviewResult(
        success=success,
        issues=parsed_issues,
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


def vim_get_quickfix_list(issues: list) -> List[dict]:
    """
    Convert issues to quickfix list format.

    Called from VimScript: py3eval('vim4rabbit.vim_get_quickfix_list(' . issues . ')')

    Args:
        issues: List of issue dicts from vim_parse_review_output

    Returns:
        List of dicts suitable for Vim's setqflist()
    """
    from .types import FileLocation

    qflist = []
    for i, issue in enumerate(issues, 1):
        if not isinstance(issue, dict):
            continue

        location = issue.get("location")
        if location and location.get("filepath"):
            qflist.append({
                "filename": location["filepath"],
                "lnum": location.get("line", 1) or 1,
                "text": issue.get("summary", f"Issue #{i}"),
                "type": "W",  # Warning type
            })

    return qflist


# =============================================================================
# Convenience function for backward compatibility
# =============================================================================


def get_message() -> str:
    """Return the iconic message (kept for backward compatibility)."""
    return "All your vim are belong to us."
