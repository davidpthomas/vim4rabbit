"""
Data types for vim4rabbit.

This module contains dataclasses used throughout the plugin.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TokenUsage:
    """Token usage tracking data."""
    used: int = 0
    limit: int = 0
    provider: str = "rabbit"

    def to_dict(self) -> dict:
        """Convert to dict for Vim serialization."""
        return {
            "used": self.used,
            "limit": self.limit,
            "provider": self.provider,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenUsage":
        """Create from dict (e.g., from JSON cache)."""
        return cls(
            used=data.get("used", 0),
            limit=data.get("limit", 0),
            provider=data.get("provider", "rabbit"),
        )

    @property
    def percentage(self) -> int:
        """Calculate usage percentage."""
        if self.limit == 0:
            return 0
        return (self.used * 100) // self.limit


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
