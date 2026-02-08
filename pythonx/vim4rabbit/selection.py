"""
Issue selection state management for vim4rabbit.

Module-level state + functions for tracking which review issues are selected.
Same pattern as games/__init__.py.
"""

import re
from typing import List, Set

# Module-level state
_selections: Set[int] = set()
_issue_count: int = 0


def init_selections(issue_count: int) -> None:
    """
    Reset state for a new review.

    Args:
        issue_count: Total number of issues in the review
    """
    global _selections, _issue_count
    _selections = set()
    _issue_count = issue_count


def reset_selections() -> None:
    """Clear all state (on cleanup)."""
    global _selections, _issue_count
    _selections = set()
    _issue_count = 0


def toggle_selection(issue_num: int) -> bool:
    """
    Toggle selection for an issue number.

    Args:
        issue_num: 1-based issue number

    Returns:
        New selection state (True = selected)
    """
    if issue_num in _selections:
        _selections.discard(issue_num)
        return False
    else:
        _selections.add(issue_num)
        return True


def select_all() -> int:
    """
    Select all issues.

    Returns:
        Number of issues selected
    """
    global _selections
    _selections = set(range(1, _issue_count + 1))
    return _issue_count


def deselect_all() -> int:
    """
    Deselect all issues.

    Returns:
        Number of issues deselected
    """
    global _selections
    count = len(_selections)
    _selections = set()
    return count


def get_selected() -> List[int]:
    """
    Get sorted list of selected issue numbers.

    Returns:
        Sorted list of 1-based issue numbers
    """
    return sorted(_selections)


def get_issue_count() -> int:
    """
    Get total number of issues.

    Returns:
        Total issue count
    """
    return _issue_count


def find_issue_at_line(lines: List[str], cursor_line_index: int) -> int:
    """
    Parse buffer lines to find issue number at cursor position.

    Searches the given line and upward for a fold header with checkbox pattern.

    Args:
        lines: Buffer lines (0-indexed list)
        cursor_line_index: 0-based line index of cursor

    Returns:
        Issue number (1-based) or 0 if not found
    """
    if not lines or cursor_line_index < 0 or cursor_line_index >= len(lines):
        return 0

    pattern = re.compile(r'^\s*\[.\]\s*(\d+)\.')
    fold_end = re.compile(r'\}\}\}')

    search_line = cursor_line_index
    while search_line >= 0:
        line = lines[search_line]
        match = pattern.match(line)
        if match:
            return int(match.group(1))
        # Stop if we hit a fold end marker (we went too far)
        if search_line < cursor_line_index and fold_end.search(line):
            break
        search_line -= 1

    return 0
