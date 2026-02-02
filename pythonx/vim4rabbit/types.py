"""
Data types for vim4rabbit.

This module contains dataclasses used throughout the plugin.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ReviewIssue:
    """A single review issue from CodeRabbit output."""
    lines: List[str] = field(default_factory=list)

    def to_list(self) -> List[str]:
        """Convert to list for Vim serialization."""
        return self.lines


@dataclass
class ReviewResult:
    """Result of running CodeRabbit review."""
    success: bool = False
    issues: List[ReviewIssue] = field(default_factory=list)
    error_message: str = ""
    raw_output: str = ""

    def to_dict(self) -> dict:
        """Convert to dict for Vim serialization."""
        return {
            "success": self.success,
            "issues": [issue.to_list() for issue in self.issues],
            "error_message": self.error_message,
        }
