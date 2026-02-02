"""
Parsing functions for vim4rabbit.

This module handles parsing of CodeRabbit CLI output.
"""

import re
from typing import List

from .types import ReviewIssue


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
                issues.append(ReviewIssue(lines=current_lines))
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
        issues.append(ReviewIssue(lines=current_lines))

    return issues
