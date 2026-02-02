"""
Token usage management for vim4rabbit.

This module handles fetching and tracking CodeRabbit token usage.
"""

from typing import Optional

from .cache import get_coderabbit_usage_file, load_token_usage, save_token_cache
from .cli import run_usage_json, run_usage_plain
from .parser import parse_usage_json, parse_usage_plain
from .types import TokenUsage


# Module-level token usage state
_current_usage: Optional[TokenUsage] = None


def get_current_usage() -> TokenUsage:
    """
    Get the current token usage.

    Returns:
        Current TokenUsage (may have zero values if not yet fetched)
    """
    global _current_usage
    if _current_usage is None:
        _current_usage = TokenUsage()
    return _current_usage


def set_current_usage(usage: TokenUsage) -> None:
    """
    Set the current token usage.

    Args:
        usage: TokenUsage to set as current
    """
    global _current_usage
    _current_usage = usage


def fetch_usage() -> Optional[TokenUsage]:
    """
    Fetch token usage from CodeRabbit CLI.

    Tries multiple methods:
    1. 'coderabbit usage --json' command
    2. 'coderabbit usage' plain text
    3. CodeRabbit config file (~/.config/coderabbit/usage.json)
    4. Our cache file (~/.vim4rabbit/usage.json)

    Ported from vim4rabbit#FetchTokenUsage().

    Returns:
        TokenUsage if fetched successfully, None otherwise
    """
    # Method 1: Try 'coderabbit usage --json' command
    json_output, success = run_usage_json()
    if success:
        usage = parse_usage_json(json_output)
        if usage:
            set_current_usage(usage)
            save_token_cache(usage)
            return usage

    # Method 2: Try 'coderabbit usage' plain text
    plain_output, success = run_usage_plain()
    if success:
        usage = parse_usage_plain(plain_output)
        if usage:
            set_current_usage(usage)
            save_token_cache(usage)
            return usage

    # Method 3: Check CodeRabbit config directory for usage file
    cr_file = get_coderabbit_usage_file()
    if cr_file:
        try:
            with open(cr_file, "r") as f:
                content = f.read()
            usage = parse_usage_json(content)
            if usage:
                set_current_usage(usage)
                save_token_cache(usage)
                return usage
        except IOError:
            pass

    # Method 4: Fall back to our cache file
    usage = load_token_usage()
    if usage:
        set_current_usage(usage)
        return usage

    return None


def get_usage_dict() -> dict:
    """
    Get current token usage as a dict for Vim.

    Returns:
        Dict with 'used', 'limit', and 'provider' keys
    """
    return get_current_usage().to_dict()


def load_cached_usage() -> Optional[TokenUsage]:
    """
    Load token usage from cache file only (no CLI calls).

    Returns:
        TokenUsage if cache exists, None otherwise
    """
    usage = load_token_usage()
    if usage:
        set_current_usage(usage)
    return usage
