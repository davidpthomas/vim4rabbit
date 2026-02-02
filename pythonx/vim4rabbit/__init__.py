"""
vim4rabbit - A Vim plugin powered by Python

This module provides the Python backend for vim4rabbit.
All vim_* functions are the public API called from VimScript via py3eval().
"""

__version__ = "0.1.0"

from typing import List

from .cli import run_review
from .content import format_loading_message, format_review_output, render_help
from .tokens import fetch_usage, get_current_usage, get_usage_dict, load_cached_usage, set_current_usage
from .types import TokenUsage


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


def vim_fetch_usage() -> dict:
    """
    Fetch token usage from CodeRabbit CLI.

    Called from VimScript: py3eval('vim4rabbit.vim_fetch_usage()')

    Returns:
        Dict with keys:
        - used: int
        - limit: int
        - provider: str
    """
    usage = fetch_usage()
    if usage:
        return usage.to_dict()
    return get_usage_dict()


def vim_load_cached_usage() -> dict:
    """
    Load token usage from cache file only.

    Called from VimScript: py3eval('vim4rabbit.vim_load_cached_usage()')

    Returns:
        Dict with 'used', 'limit', 'provider' keys
    """
    usage = load_cached_usage()
    if usage:
        return usage.to_dict()
    return get_usage_dict()


def vim_get_usage() -> dict:
    """
    Get current token usage (from memory).

    Called from VimScript: py3eval('vim4rabbit.vim_get_usage()')

    Returns:
        Dict with 'used', 'limit', 'provider' keys
    """
    return get_usage_dict()


def vim_set_usage(used: int, limit: int, provider: str = "rabbit") -> dict:
    """
    Set token usage directly.

    Called from VimScript: py3eval('vim4rabbit.vim_set_usage(...)')

    Args:
        used: Tokens used
        limit: Token limit
        provider: Provider name

    Returns:
        Dict with updated values
    """
    usage = TokenUsage(used=used, limit=limit, provider=provider)
    set_current_usage(usage)
    return usage.to_dict()


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
    usage_used: int = 0,
    usage_limit: int = 0,
) -> List[str]:
    """
    Format review results for display.

    Called from VimScript after vim_run_review().

    Args:
        success: Whether review succeeded
        issues: List of issues (each issue is list of line strings)
        error_message: Error message if failed
        usage_used: Token usage (used)
        usage_limit: Token usage (limit)

    Returns:
        List of strings (lines) for the review buffer
    """
    from .types import ReviewIssue, ReviewResult

    result = ReviewResult(
        success=success,
        issues=[ReviewIssue(lines=issue) for issue in issues],
        error_message=error_message,
    )

    usage = None
    if usage_limit > 0:
        usage = TokenUsage(used=usage_used, limit=usage_limit)

    return format_review_output(result, usage)


def vim_get_loading_content() -> List[str]:
    """
    Get the loading message content.

    Called from VimScript: py3eval('vim4rabbit.vim_get_loading_content()')

    Returns:
        List of strings for loading state
    """
    return format_loading_message()


# =============================================================================
# Convenience function for backward compatibility
# =============================================================================


def get_message() -> str:
    """Return the iconic message (kept for backward compatibility)."""
    return "All your vim are belong to us."
