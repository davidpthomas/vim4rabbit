"""Tests for vim4rabbit.parser module."""

import pytest
from vim4rabbit.parser import parse_review_issues


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
