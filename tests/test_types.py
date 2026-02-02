"""Tests for vim4rabbit.types module."""

import pytest
from vim4rabbit.types import TokenUsage, ReviewIssue, ReviewResult


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        usage = TokenUsage()
        assert usage.used == 0
        assert usage.limit == 0
        assert usage.provider == "rabbit"

    def test_custom_values(self):
        """Test custom initialization."""
        usage = TokenUsage(used=5000, limit=10000, provider="coderabbit")
        assert usage.used == 5000
        assert usage.limit == 10000
        assert usage.provider == "coderabbit"

    def test_to_dict(self):
        """Test conversion to dict."""
        usage = TokenUsage(used=5000, limit=10000, provider="coderabbit")
        d = usage.to_dict()
        assert d == {"used": 5000, "limit": 10000, "provider": "coderabbit"}

    def test_from_dict(self):
        """Test creation from dict."""
        data = {"used": 5000, "limit": 10000, "provider": "coderabbit"}
        usage = TokenUsage.from_dict(data)
        assert usage.used == 5000
        assert usage.limit == 10000
        assert usage.provider == "coderabbit"

    def test_from_dict_partial(self):
        """Test creation from partial dict."""
        usage = TokenUsage.from_dict({"used": 100})
        assert usage.used == 100
        assert usage.limit == 0
        assert usage.provider == "rabbit"

    def test_percentage_normal(self):
        """Test percentage calculation."""
        usage = TokenUsage(used=4500, limit=10000)
        assert usage.percentage == 45

    def test_percentage_zero_limit(self):
        """Test percentage with zero limit."""
        usage = TokenUsage(used=100, limit=0)
        assert usage.percentage == 0

    def test_percentage_full(self):
        """Test percentage at 100%."""
        usage = TokenUsage(used=10000, limit=10000)
        assert usage.percentage == 100


class TestReviewIssue:
    """Tests for ReviewIssue dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        issue = ReviewIssue()
        assert issue.lines == []

    def test_with_lines(self):
        """Test with content."""
        lines = ["Line 1", "Line 2"]
        issue = ReviewIssue(lines=lines)
        assert issue.lines == lines

    def test_to_list(self):
        """Test conversion to list."""
        lines = ["Line 1", "Line 2"]
        issue = ReviewIssue(lines=lines)
        assert issue.to_list() == lines


class TestReviewResult:
    """Tests for ReviewResult dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        result = ReviewResult()
        assert result.success is False
        assert result.issues == []
        assert result.error_message == ""
        assert result.raw_output == ""

    def test_success_with_issues(self):
        """Test successful result with issues."""
        issues = [ReviewIssue(lines=["Issue 1"]), ReviewIssue(lines=["Issue 2"])]
        result = ReviewResult(success=True, issues=issues)
        assert result.success is True
        assert len(result.issues) == 2

    def test_to_dict(self):
        """Test conversion to dict."""
        issues = [ReviewIssue(lines=["Line 1", "Line 2"])]
        result = ReviewResult(success=True, issues=issues, error_message="")
        d = result.to_dict()
        assert d["success"] is True
        assert d["issues"] == [["Line 1", "Line 2"]]
        assert d["error_message"] == ""

    def test_error_result(self):
        """Test error result."""
        result = ReviewResult(success=False, error_message="Command not found")
        d = result.to_dict()
        assert d["success"] is False
        assert d["error_message"] == "Command not found"
        assert d["issues"] == []
