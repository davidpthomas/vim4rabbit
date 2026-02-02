"""Tests for vim4rabbit.types module."""

import pytest
from vim4rabbit.types import ReviewIssue, ReviewResult


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
