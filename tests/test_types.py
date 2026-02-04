"""Tests for vim4rabbit.types module."""

import pytest
from vim4rabbit.types import FileLocation, ReviewIssue, ReviewResult


class TestFileLocation:
    """Tests for FileLocation dataclass."""

    def test_with_line(self):
        """Test with line number."""
        loc = FileLocation(filepath="src/main.py", line=42)
        assert loc.filepath == "src/main.py"
        assert loc.line == 42

    def test_without_line(self):
        """Test without line number."""
        loc = FileLocation(filepath="src/main.py")
        assert loc.filepath == "src/main.py"
        assert loc.line is None

    def test_to_dict(self):
        """Test conversion to dict."""
        loc = FileLocation(filepath="src/main.py", line=42)
        d = loc.to_dict()
        assert d == {"filepath": "src/main.py", "line": 42}


class TestReviewIssue:
    """Tests for ReviewIssue dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        issue = ReviewIssue()
        assert issue.lines == []
        assert issue.location is None
        assert issue.summary == ""

    def test_with_lines(self):
        """Test with content."""
        lines = ["Line 1", "Line 2"]
        issue = ReviewIssue(lines=lines)
        assert issue.lines == lines

    def test_with_location(self):
        """Test with file location."""
        loc = FileLocation(filepath="src/main.py", line=42)
        issue = ReviewIssue(lines=["Error"], location=loc, summary="An error")
        assert issue.location == loc
        assert issue.summary == "An error"

    def test_to_list(self):
        """Test conversion to list."""
        lines = ["Line 1", "Line 2"]
        issue = ReviewIssue(lines=lines)
        assert issue.to_list() == lines

    def test_to_dict_with_location(self):
        """Test to_dict with location."""
        loc = FileLocation(filepath="src/main.py", line=42)
        issue = ReviewIssue(lines=["Error here"], location=loc, summary="An error")
        d = issue.to_dict()
        assert d["lines"] == ["Error here"]
        assert d["location"] == {"filepath": "src/main.py", "line": 42}
        assert d["summary"] == "An error"

    def test_to_dict_without_location(self):
        """Test to_dict without location."""
        issue = ReviewIssue(lines=["General warning"])
        d = issue.to_dict()
        assert d["lines"] == ["General warning"]
        assert d["location"] is None
        assert d["summary"] == ""


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
        loc = FileLocation(filepath="main.py", line=10)
        issues = [ReviewIssue(lines=["Line 1", "Line 2"], location=loc, summary="Issue")]
        result = ReviewResult(success=True, issues=issues, error_message="")
        d = result.to_dict()
        assert d["success"] is True
        assert len(d["issues"]) == 1
        assert d["issues"][0]["lines"] == ["Line 1", "Line 2"]
        assert d["issues"][0]["location"] == {"filepath": "main.py", "line": 10}
        assert d["error_message"] == ""

    def test_error_result(self):
        """Test error result."""
        result = ReviewResult(success=False, error_message="Command not found")
        d = result.to_dict()
        assert d["success"] is False
        assert d["error_message"] == "Command not found"
        assert d["issues"] == []
