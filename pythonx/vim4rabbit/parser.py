"""
Parsing functions for vim4rabbit.

This module handles parsing of CodeRabbit CLI output.
"""

import re
from typing import List, Optional, Tuple

from .types import FileLocation, ReviewIssue


# Patterns to match file:line references in CodeRabbit output
FILE_LINE_PATTERNS = [
    # "File: path/to/file.py:42" or "File: path/to/file.py (line 42)"
    re.compile(r"^(?:File:\s*)?([^\s:]+):(\d+)"),
    # "path/to/file.py:42:" at start of line
    re.compile(r"^([^\s:]+):(\d+):"),
    # "in path/to/file.py at line 42"
    re.compile(r"in\s+([^\s]+)\s+at\s+line\s+(\d+)", re.IGNORECASE),
    # "path/to/file.py (line 42)" or "path/to/file.py (lines 42-50)"
    re.compile(r"([^\s]+\.(?:py|js|ts|tsx|jsx|go|rs|rb|java|cpp|c|h))\s*\(lines?\s*(\d+)"),
]


def extract_file_location(lines: List[str]) -> Optional[FileLocation]:
    """
    Extract file:line location from issue lines.

    Args:
        lines: Lines of the issue text

    Returns:
        FileLocation if found, None otherwise
    """
    for line in lines:
        for pattern in FILE_LINE_PATTERNS:
            match = pattern.search(line)
            if match:
                filepath = match.group(1)
                line_num = int(match.group(2))
                return FileLocation(filepath=filepath, line=line_num)
    return None


def extract_summary(lines: List[str]) -> str:
    """
    Extract a summary from issue lines.

    Uses the first non-empty, non-file-reference line.

    Args:
        lines: Lines of the issue text

    Returns:
        Summary string (first meaningful line)
    """
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip lines that look like file references
        if stripped.startswith("File:") or re.match(r"^[^\s:]+:\d+:", stripped):
            continue
        # Skip separator lines
        if re.match(r"^[-=]{3,}$", stripped):
            continue
        return stripped[:100]  # Truncate long summaries
    return ""


def parse_review_issues(output: str) -> List[ReviewIssue]:
    """
    Parse review output into separate issues.

    Issues are separated by lines containing multiple equal signs (=====).
    Ported from vim4rabbit#ParseReviewIssues().

    Args:
        output: Raw output from CodeRabbit CLI

    Returns:
        List of ReviewIssue objects
    """
    issues: List[ReviewIssue] = []
    current_lines: List[str] = []
    in_issue = False

    for line in output.split("\n"):
        # Check if this is a separator line (5+ equal signs)
        if re.match(r"^={5,}\s*$", line):
            # If we were collecting an issue, save it
            if in_issue and current_lines:
                location = extract_file_location(current_lines)
                summary = extract_summary(current_lines)
                issues.append(ReviewIssue(
                    lines=current_lines,
                    location=location,
                    summary=summary,
                ))
            # Start a new issue
            current_lines = []
            in_issue = True
        elif in_issue:
            # Add line to current issue (trim trailing whitespace)
            current_lines.append(line.rstrip())
        else:
            # Content before first separator - could be header/summary
            # Start collecting as first issue if non-empty
            if line.strip():
                in_issue = True
                current_lines.append(line.rstrip())

    # Don't forget the last issue
    if current_lines:
        location = extract_file_location(current_lines)
        summary = extract_summary(current_lines)
        issues.append(ReviewIssue(
            lines=current_lines,
            location=location,
            summary=summary,
        ))

    return issues
