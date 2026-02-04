"""
Data types for vim4rabbit.

This module contains dataclasses used throughout the plugin.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileLocation:
    """A file location with optional line number."""
    filepath: str
    line: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dict for Vim serialization."""
        return {
            "filepath": self.filepath,
            "line": self.line,
        }


@dataclass
class ReviewIssue:
    """A single review issue from CodeRabbit output."""
    lines: List[str] = field(default_factory=list)
    location: Optional[FileLocation] = None
    summary: str = ""

    def to_list(self) -> List[str]:
        """Convert to list for Vim serialization."""
        return self.lines

    def to_dict(self) -> dict:
        """Convert to dict for Vim serialization."""
        return {
            "lines": self.lines,
            "location": self.location.to_dict() if self.location else None,
            "summary": self.summary,
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
            "issues": [issue.to_dict() for issue in self.issues],
            "error_message": self.error_message,
        }
