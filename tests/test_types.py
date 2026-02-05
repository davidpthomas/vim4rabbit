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

    def test_to_dict(self):
        """Test conversion to dict with full metadata."""
        issue = ReviewIssue(
            lines=["Line 1", "Line 2"],
            file_path="src/main.py",
            line_range="10-20",
            issue_type="potential_issue",
            summary="Test summary",
            prompt="Fix the issue at line 10",
        )
        d = issue.to_dict()
        assert d["lines"] == ["Line 1", "Line 2"]
        assert d["file_path"] == "src/main.py"
        assert d["line_range"] == "10-20"
        assert d["issue_type"] == "potential_issue"
        assert d["summary"] == "Test summary"
        assert d["prompt"] == "Fix the issue at line 10"

    def test_prompt_field(self):
        """Test prompt field initialization."""
        issue = ReviewIssue(prompt="Fix this bug")
        assert issue.prompt == "Fix this bug"


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
        assert "issues_data" in d
        assert len(d["issues_data"]) == 1
        assert d["issues_data"][0]["lines"] == ["Line 1", "Line 2"]

    def test_error_result(self):
        """Test error result."""
        result = ReviewResult(success=False, error_message="Command not found")
        d = result.to_dict()
        assert d["success"] is False
        assert d["error_message"] == "Command not found"
        assert d["issues"] == []
