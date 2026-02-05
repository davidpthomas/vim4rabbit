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
    file_path: str = ""
    line_range: str = ""
    issue_type: str = ""
    summary: str = ""
    prompt: str = ""  # AI prompt for implementing the fix

    def to_list(self) -> List[str]:
        """Convert to list for Vim serialization."""
        return self.lines

    def to_dict(self) -> dict:
        """Convert to dict for Vim serialization with full metadata."""
        return {
            "lines": self.lines,
            "file_path": self.file_path,
            "line_range": self.line_range,
            "issue_type": self.issue_type,
            "summary": self.summary,
            "prompt": self.prompt,
        }


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
            "issues_data": [issue.to_dict() for issue in self.issues],
            "error_message": self.error_message,
        }
