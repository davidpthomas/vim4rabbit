"""Tests for vim4rabbit.parser module."""

import pytest
from vim4rabbit.parser import (
    extract_file_location,
    extract_summary,
    parse_review_issues,
)


class TestParseReviewIssues:
    """Tests for parse_review_issues function."""

    def test_empty_output(self):
        """Test with empty output."""
        issues = parse_review_issues("")
        assert issues == []

    def test_single_issue_no_separator(self):
        """Test single issue without separator."""
        output = "This is an issue\nWith multiple lines"
        issues = parse_review_issues(output)
        assert len(issues) == 1
        assert issues[0].lines == ["This is an issue", "With multiple lines"]

    def test_multiple_issues_with_separator(self):
        """Test multiple issues separated by equal signs."""
        output = """First issue
=====
Second issue
line 2
=====
Third issue"""
        issues = parse_review_issues(output)
        assert len(issues) == 3
        assert issues[0].lines == ["First issue"]
        assert issues[1].lines == ["Second issue", "line 2"]
        assert issues[2].lines == ["Third issue"]

    def test_trailing_whitespace_stripped(self):
        """Test that trailing whitespace is stripped."""
        output = "Issue line   \n=====\nAnother   "
        issues = parse_review_issues(output)
        assert issues[0].lines == ["Issue line"]
        assert issues[1].lines == ["Another"]

    def test_long_separator(self):
        """Test with longer separator line."""
        output = "Issue 1\n" + "=" * 50 + "\nIssue 2"
        issues = parse_review_issues(output)
        assert len(issues) == 2

    def test_whitespace_only_lines_before_content(self):
        """Test that leading blank lines are skipped."""
        output = "\n\n  \nActual issue"
        issues = parse_review_issues(output)
        assert len(issues) == 1
        assert issues[0].lines == ["Actual issue"]

    def test_issue_with_file_location(self):
        """Test that file locations are extracted."""
        output = "src/main.py:42: Some issue\n=====\nFile: lib/utils.py:10\nAnother issue"
        issues = parse_review_issues(output)
        assert len(issues) == 2
        assert issues[0].location is not None
        assert issues[0].location.filepath == "src/main.py"
        assert issues[0].location.line == 42
        assert issues[1].location is not None
        assert issues[1].location.filepath == "lib/utils.py"
        assert issues[1].location.line == 10

    def test_issue_without_file_location(self):
        """Test issues without file locations."""
        output = "General warning about the code"
        issues = parse_review_issues(output)
        assert len(issues) == 1
        assert issues[0].location is None


class TestExtractFileLocation:
    """Tests for extract_file_location function."""

    def test_file_colon_line_colon_format(self):
        """Test path:line: format."""
        lines = ["src/main.py:42: Error here"]
        location = extract_file_location(lines)
        assert location is not None
        assert location.filepath == "src/main.py"
        assert location.line == 42

    def test_file_prefix_format(self):
        """Test File: path:line format."""
        lines = ["File: lib/utils.py:10", "Some description"]
        location = extract_file_location(lines)
        assert location is not None
        assert location.filepath == "lib/utils.py"
        assert location.line == 10

    def test_in_at_line_format(self):
        """Test 'in path at line N' format."""
        lines = ["Found issue in src/helper.py at line 25"]
        location = extract_file_location(lines)
        assert location is not None
        assert location.filepath == "src/helper.py"
        assert location.line == 25

    def test_parenthetical_line_format(self):
        """Test path.py (line N) format."""
        lines = ["Check module.py (line 100) for issues"]
        location = extract_file_location(lines)
        assert location is not None
        assert location.filepath == "module.py"
        assert location.line == 100

    def test_no_file_location(self):
        """Test with no file location."""
        lines = ["This is just a general warning", "No file reference here"]
        location = extract_file_location(lines)
        assert location is None


class TestExtractSummary:
    """Tests for extract_summary function."""

    def test_simple_summary(self):
        """Test extracting a simple summary."""
        lines = ["This is the main issue", "More details here"]
        summary = extract_summary(lines)
        assert summary == "This is the main issue"

    def test_skip_file_reference(self):
        """Test that file references are skipped."""
        lines = ["File: src/main.py:42", "Actual summary here"]
        summary = extract_summary(lines)
        assert summary == "Actual summary here"

    def test_skip_separator_lines(self):
        """Test that separator lines are skipped."""
        lines = ["---", "===", "Real summary"]
        summary = extract_summary(lines)
        assert summary == "Real summary"

    def test_empty_lines(self):
        """Test with empty lines."""
        lines = ["", "", "Summary after blanks"]
        summary = extract_summary(lines)
        assert summary == "Summary after blanks"

    def test_truncate_long_summary(self):
        """Test that long summaries are truncated."""
        long_text = "A" * 150
        lines = [long_text]
        summary = extract_summary(lines)
        assert len(summary) == 100
