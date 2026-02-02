"""
File caching operations for vim4rabbit.

This module handles reading and writing token usage cache files.
"""

import json
import os
from pathlib import Path
from typing import Optional

from .types import TokenUsage


def get_cache_dir() -> Path:
    """Get the vim4rabbit cache directory path."""
    return Path.home() / ".vim4rabbit"


def get_cache_file() -> Path:
    """Get the token usage cache file path."""
    return get_cache_dir() / "usage.json"


def load_token_usage() -> Optional[TokenUsage]:
    """
    Load token usage from cache file (~/.vim4rabbit/usage.json).

    Expected format: {"used": 12345, "limit": 100000, "provider": "coderabbit"}

    Ported from vim4rabbit#LoadTokenUsage().

    Returns:
        TokenUsage object if cache exists and is valid, None otherwise
    """
    cache_file = get_cache_file()

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return TokenUsage.from_dict(data)
    except (json.JSONDecodeError, IOError, KeyError):
        pass

    return None


def save_token_cache(usage: TokenUsage) -> bool:
    """
    Save token usage to cache file for persistence.

    Ported from vim4rabbit#SaveTokenCache().

    Args:
        usage: TokenUsage object to save

    Returns:
        True if save succeeded, False otherwise
    """
    cache_dir = get_cache_dir()
    cache_file = get_cache_file()

    try:
        # Create directory if needed
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Write cache file
        with open(cache_file, "w") as f:
            json.dump(usage.to_dict(), f)

        return True
    except (IOError, OSError):
        return False


def get_coderabbit_usage_file() -> Optional[Path]:
    """
    Get the CodeRabbit config usage file path if it exists.

    Returns:
        Path to ~/.config/coderabbit/usage.json if it exists, None otherwise
    """
    cr_file = Path.home() / ".config" / "coderabbit" / "usage.json"
    if cr_file.exists():
        return cr_file
    return None
