"""
Parsing functions for vim4rabbit.

This module handles parsing of CodeRabbit CLI output and usage data.
"""

import json
import re
from typing import List, Optional, Tuple

from .types import ReviewIssue, TokenUsage


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


def parse_usage_json(json_str: str) -> Optional[TokenUsage]:
    """
    Parse JSON usage output from CodeRabbit.

    Supports multiple JSON structures:
    - {"used": 12345, "limit": 100000}
    - {"usage": {"tokens_used": 12345, "tokens_limit": 100000}}
    - {"plan": {"usage": 12345, "limit": 100000}}
    - {"tokens_used": 12345, "tokens_limit": 100000}

    Ported from vim4rabbit#ParseUsageJson().

    Args:
        json_str: JSON string from CodeRabbit CLI

    Returns:
        TokenUsage object if parsing succeeds, None otherwise
    """
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            return None

        used = 0
        limit = 0

        # Try different JSON structures
        if "used" in data and "limit" in data:
            used = data["used"]
            limit = data["limit"]
        elif "usage" in data and isinstance(data["usage"], dict):
            usage = data["usage"]
            used = usage.get("tokens_used", usage.get("used", 0))
            limit = usage.get("tokens_limit", usage.get("limit", 0))
        elif "plan" in data and isinstance(data["plan"], dict):
            plan = data["plan"]
            used = plan.get("usage", plan.get("used", 0))
            limit = plan.get("limit", 0)
        elif "tokens_used" in data and "tokens_limit" in data:
            used = data["tokens_used"]
            limit = data["tokens_limit"]

        if limit > 0:
            return TokenUsage(used=used, limit=limit, provider="coderabbit")

        return None
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def parse_usage_plain(text: str) -> Optional[TokenUsage]:
    """
    Parse plain text usage output from CodeRabbit.

    Looks for patterns like:
    - "Used: 12,345 / 100,000 tokens"
    - "Usage: 45%"
    - "12345/100000"
    - "tokens_used: 12345" and "tokens_limit: 100000"

    Ported from vim4rabbit#ParseUsagePlain().

    Args:
        text: Plain text output from CodeRabbit CLI

    Returns:
        TokenUsage object if parsing succeeds, None otherwise
    """
    used = 0
    limit = 0

    # Pattern: "Used: 12,345 / 100,000" or "12345 / 100000"
    match = re.search(r"(\d[\d,]*)\s*/\s*(\d[\d,]*)", text)
    if match:
        used = int(match.group(1).replace(",", ""))
        limit = int(match.group(2).replace(",", ""))

    # Pattern: "tokens_used: 12345" and "tokens_limit: 100000"
    if limit == 0:
        used_match = re.search(r"tokens?[_\s]*used[:\s]+(\d[\d,]*)", text, re.IGNORECASE)
        limit_match = re.search(r"tokens?[_\s]*limit[:\s]+(\d[\d,]*)", text, re.IGNORECASE)
        if used_match and limit_match:
            used = int(used_match.group(1).replace(",", ""))
            limit = int(limit_match.group(1).replace(",", ""))

    if limit > 0:
        return TokenUsage(used=used, limit=limit, provider="coderabbit")

    return None


def parse_usage(json_str: str = "", plain_text: str = "") -> Optional[TokenUsage]:
    """
    Try to parse usage from JSON first, then plain text.

    Args:
        json_str: JSON string to try first
        plain_text: Plain text to try as fallback

    Returns:
        TokenUsage object if parsing succeeds, None otherwise
    """
    if json_str:
        result = parse_usage_json(json_str)
        if result:
            return result

    if plain_text:
        return parse_usage_plain(plain_text)

    return None
