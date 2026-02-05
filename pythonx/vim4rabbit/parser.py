"""
Parsing functions for vim4rabbit.

This module handles parsing of CodeRabbit CLI output.
"""

import re
from typing import Dict, List

from .types import ReviewIssue


def parse_issue_metadata(lines: List[str]) -> Dict[str, str]:
    """
    Extract metadata from issue lines.

    Looks for patterns like:
    - File: path/to/file.py
    - Line: 123 to 456 (or Line: 123)
    - Type: potential_issue
    - Comment: first line after this becomes the summary

    Args:
        lines: List of lines from a single issue

    Returns:
        Dict with keys: file_path, line_range, issue_type, summary
    """
    metadata: Dict[str, str] = {
        "file_path": "",
        "line_range": "",
        "issue_type": "",
        "summary": "",
    }

    in_comment = False
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Extract File:
        if stripped.startswith("File:"):
            metadata["file_path"] = stripped[5:].strip()
            continue

        # Extract Line: (handles "Line: X" and "Line: X to Y")
        if stripped.startswith("Line:"):
            line_text = stripped[5:].strip()
            # Normalize "X to Y" to "X-Y"
            line_text = re.sub(r"(\d+)\s+to\s+(\d+)", r"\1-\2", line_text)
            metadata["line_range"] = line_text
            continue

        # Extract Type:
        if stripped.startswith("Type:"):
            metadata["issue_type"] = stripped[5:].strip()
            continue

        # Extract summary from first non-empty line after "Comment:"
        if stripped.startswith("Comment:"):
            in_comment = True
            # Check if there's text on the same line as "Comment:"
            comment_text = stripped[8:].strip()
            if comment_text:
                metadata["summary"] = comment_text
                in_comment = False
            continue

        if in_comment and stripped:
            metadata["summary"] = stripped
            in_comment = False

    # Fallback: if no summary found, use first non-empty line
    if not metadata["summary"]:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(("File:", "Line:", "Type:", "Comment:")):
                metadata["summary"] = stripped
                break

    # Truncate summary if too long
    if len(metadata["summary"]) > 60:
        metadata["summary"] = metadata["summary"][:57] + "..."

    return metadata


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

    # Extract metadata for each issue
    for issue in issues:
        metadata = parse_issue_metadata(issue.lines)
        issue.file_path = metadata["file_path"]
        issue.line_range = metadata["line_range"]
        issue.issue_type = metadata["issue_type"]
        issue.summary = metadata["summary"]

    return issues
