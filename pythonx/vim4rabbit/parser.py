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
    - Prompt: AI-actionable prompt for implementing the fix

    Args:
        lines: List of lines from a single issue

    Returns:
        Dict with keys: file_path, line_range, issue_type, summary, prompt
    """
    metadata: Dict[str, str] = {
        "file_path": "",
        "line_range": "",
        "issue_type": "",
        "summary": "",
        "prompt": "",
    }

    in_comment = False
    in_prompt = False
    prompt_lines: List[str] = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Extract File:
        if stripped.startswith("File:"):
            metadata["file_path"] = stripped[5:].strip()
            in_prompt = False
            continue

        # Extract Line: (handles "Line: X" and "Line: X to Y")
        if stripped.startswith("Line:"):
            line_text = stripped[5:].strip()
            # Normalize "X to Y" to "X-Y"
            line_text = re.sub(r"(\d+)\s+to\s+(\d+)", r"\1-\2", line_text)
            metadata["line_range"] = line_text
            in_prompt = False
            continue

        # Extract Type:
        if stripped.startswith("Type:"):
            metadata["issue_type"] = stripped[5:].strip()
            in_prompt = False
            continue

        # Extract summary from first non-empty line after "Comment:"
        if stripped.startswith("Comment:"):
            in_comment = True
            in_prompt = False
            # Check if there's text on the same line as "Comment:"
            comment_text = stripped[8:].strip()
            if comment_text:
                metadata["summary"] = comment_text
                in_comment = False
            continue

        # Extract Prompt: (may be multi-line)
        if stripped.startswith("Prompt:"):
            in_prompt = True
            in_comment = False
            # Check if there's text on the same line as "Prompt:"
            prompt_text = stripped[7:].strip()
            if prompt_text:
                prompt_lines.append(prompt_text)
            continue

        if in_comment and stripped:
            metadata["summary"] = stripped
            in_comment = False
            continue

        # Continue collecting prompt lines until we hit another field
        if in_prompt:
            if stripped:
                prompt_lines.append(stripped)

    # Join prompt lines
    metadata["prompt"] = "\n".join(prompt_lines)

    # Fallback: if no summary found, use first non-empty line
    if not metadata["summary"]:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(
                ("File:", "Line:", "Type:", "Comment:", "Prompt:")
            ):
                metadata["summary"] = stripped
                break

    # Truncate summary if too long
    if len(metadata["summary"]) > 60:
        metadata["summary"] = metadata["summary"][:57] + "..."

    return metadata


def is_preamble_line(line: str) -> bool:
    """
    Check if a line is part of the CLI preamble (status messages to filter out).

    Args:
        line: A line of text from CLI output

    Returns:
        True if this line should be filtered out as preamble
    """
    preamble_patterns = [
        "running",
        "analyzing",
        "processing",
        "loading",
        "fetching",
        "please wait",
        "in progress",
        "starting coderabbit",
        "connecting",
        "setting up",
        "reviewing",
        "review completed",
    ]
    line_lower = line.lower().strip()
    return any(pattern in line_lower for pattern in preamble_patterns)


def parse_review_issues(output: str) -> List[ReviewIssue]:
    """
    Parse review output into separate issues.

    Issues are separated by lines containing multiple equal signs (=====).
    Preamble content (Running/Analyzing status messages) is filtered out.
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
            # Content before first separator - filter out preamble
            # Only start collecting if it's not a preamble line
            if line.strip() and not is_preamble_line(line):
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
        issue.prompt = metadata["prompt"]

    return issues
