"""Tests for vim4rabbit.parser module."""

import pytest
from vim4rabbit.parser import (
    parse_review_issues,
    parse_usage_json,
    parse_usage_plain,
    parse_usage,
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


class TestParseUsageJson:
    """Tests for parse_usage_json function."""

    def test_direct_format(self):
        """Test direct used/limit format."""
        json_str = '{"used": 5000, "limit": 10000}'
        usage = parse_usage_json(json_str)
        assert usage is not None
        assert usage.used == 5000
        assert usage.limit == 10000
        assert usage.provider == "coderabbit"

    def test_nested_usage_format(self):
        """Test nested usage format with tokens_used/tokens_limit."""
        json_str = '{"usage": {"tokens_used": 3000, "tokens_limit": 8000}}'
        usage = parse_usage_json(json_str)
        assert usage is not None
        assert usage.used == 3000
        assert usage.limit == 8000

    def test_plan_format(self):
        """Test plan format."""
        json_str = '{"plan": {"usage": 2000, "limit": 5000}}'
        usage = parse_usage_json(json_str)
        assert usage is not None
        assert usage.used == 2000
        assert usage.limit == 5000

    def test_tokens_used_tokens_limit_format(self):
        """Test tokens_used/tokens_limit at root level."""
        json_str = '{"tokens_used": 1500, "tokens_limit": 3000}'
        usage = parse_usage_json(json_str)
        assert usage is not None
        assert usage.used == 1500
        assert usage.limit == 3000

    def test_invalid_json(self):
        """Test with invalid JSON."""
        usage = parse_usage_json("not json")
        assert usage is None

    def test_empty_string(self):
        """Test with empty string."""
        usage = parse_usage_json("")
        assert usage is None

    def test_zero_limit(self):
        """Test that zero limit returns None."""
        json_str = '{"used": 100, "limit": 0}'
        usage = parse_usage_json(json_str)
        assert usage is None

    def test_non_dict_json(self):
        """Test with JSON array."""
        usage = parse_usage_json("[1, 2, 3]")
        assert usage is None


class TestParseUsagePlain:
    """Tests for parse_usage_plain function."""

    def test_slash_format(self):
        """Test 'used / limit' format."""
        text = "Used: 5000 / 10000 tokens"
        usage = parse_usage_plain(text)
        assert usage is not None
        assert usage.used == 5000
        assert usage.limit == 10000

    def test_comma_separated_numbers(self):
        """Test numbers with commas."""
        text = "12,345 / 100,000"
        usage = parse_usage_plain(text)
        assert usage is not None
        assert usage.used == 12345
        assert usage.limit == 100000

    def test_tokens_used_tokens_limit_pattern(self):
        """Test tokens_used/tokens_limit pattern."""
        text = "tokens_used: 5000\ntokens_limit: 10000"
        usage = parse_usage_plain(text)
        assert usage is not None
        assert usage.used == 5000
        assert usage.limit == 10000

    def test_token_used_token_limit_singular(self):
        """Test singular form (token_used)."""
        text = "token used: 3,000\ntoken limit: 8,000"
        usage = parse_usage_plain(text)
        assert usage is not None
        assert usage.used == 3000
        assert usage.limit == 8000

    def test_no_match(self):
        """Test with no matching pattern."""
        text = "No usage information here"
        usage = parse_usage_plain(text)
        assert usage is None

    def test_empty_string(self):
        """Test with empty string."""
        usage = parse_usage_plain("")
        assert usage is None


class TestParseUsage:
    """Tests for parse_usage convenience function."""

    def test_json_preferred(self):
        """Test that JSON is tried first."""
        json_str = '{"used": 1000, "limit": 2000}'
        plain = "3000 / 4000"
        usage = parse_usage(json_str=json_str, plain_text=plain)
        assert usage is not None
        assert usage.used == 1000
        assert usage.limit == 2000

    def test_fallback_to_plain(self):
        """Test fallback to plain text when JSON fails."""
        json_str = "invalid json"
        plain = "5000 / 10000"
        usage = parse_usage(json_str=json_str, plain_text=plain)
        assert usage is not None
        assert usage.used == 5000
        assert usage.limit == 10000

    def test_no_input(self):
        """Test with no input."""
        usage = parse_usage()
        assert usage is None
