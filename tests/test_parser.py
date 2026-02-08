"""Tests for vim4rabbit.parser module."""

import pytest
from vim4rabbit.parser import parse_review_issues, parse_issue_metadata, is_preamble_line


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


class TestIsPreambleLine:
    """Tests for is_preamble_line function."""

    @pytest.mark.parametrize("line", [
        "Starting CodeRabbit review in plain text mode...",
        "Connecting to review service",
        "Setting up",
        "Analyzing",
        "Reviewing",
        "Review completed",
        "Running",
        "Processing",
        "Loading",
        "Fetching",
        "Please wait",
        "In progress",
    ])
    def test_preamble_lines_detected(self, line):
        """Test that all known preamble lines are detected."""
        assert is_preamble_line(line) is True

    @pytest.mark.parametrize("line", [
        "File: src/main.py",
        "Comment: Fix this bug",
        "Type: potential_issue",
        "This is actual issue content",
    ])
    def test_non_preamble_lines_not_detected(self, line):
        """Test that issue content is not falsely detected as preamble."""
        assert is_preamble_line(line) is False


class TestParseReviewIssuesPreambleFiltering:
    """Tests for preamble filtering in parse_review_issues (V4R-48)."""

    def test_coderabbit_preamble_filtered_before_separator(self):
        """Test that CodeRabbit CLI preamble is not parsed as an issue."""
        output = (
            "Starting CodeRabbit review in plain text mode...\n"
            "Connecting to review service\n"
            "Setting up\n"
            "Analyzing\n"
            "Reviewing\n"
            "============================================================================\n"
            "File: autoload/vim4rabbit.vim\n"
            "Line: 219 to 228\n"
            "Type: potential_issue\n"
            "Comment: Remove debug logging\n"
        )
        issues = parse_review_issues(output)
        assert len(issues) == 1
        assert issues[0].file_path == "autoload/vim4rabbit.vim"
        assert issues[0].summary == "Remove debug logging"

    def test_preamble_only_output_produces_no_issues(self):
        """Test that output containing only preamble produces no issues."""
        output = (
            "Starting CodeRabbit review in plain text mode...\n"
            "Connecting to review service\n"
            "Setting up\n"
            "Analyzing\n"
            "Reviewing\n"
            "Review completed\n"
        )
        issues = parse_review_issues(output)
        assert issues == []


class TestParseIssueMetadata:
    """Tests for parse_issue_metadata function."""

    def test_extract_prompt_single_line(self):
        """Test extracting single-line prompt."""
        lines = [
            "File: src/main.py",
            "Line: 10",
            "Type: potential_issue",
            "Comment: Fix this bug",
            "Prompt: Update the function to handle null values",
        ]
        metadata = parse_issue_metadata(lines)
        assert metadata["prompt"] == "Update the function to handle null values"
        assert metadata["file_path"] == "src/main.py"
        assert metadata["line_range"] == "10"

    def test_extract_prompt_multiline(self):
        """Test extracting multi-line prompt."""
        lines = [
            "File: src/main.py",
            "Prompt: First line of prompt",
            "Second line of prompt",
            "Third line of prompt",
        ]
        metadata = parse_issue_metadata(lines)
        assert "First line of prompt" in metadata["prompt"]
        assert "Second line of prompt" in metadata["prompt"]
        assert "Third line of prompt" in metadata["prompt"]

    def test_prompt_ends_at_next_field(self):
        """Test that prompt collection stops at next field."""
        lines = [
            "Prompt: Fix the issue",
            "More prompt text",
            "File: src/other.py",
            "Line: 20",
        ]
        metadata = parse_issue_metadata(lines)
        assert "Fix the issue" in metadata["prompt"]
        assert "More prompt text" in metadata["prompt"]
        assert "src/other.py" not in metadata["prompt"]
        assert metadata["file_path"] == "src/other.py"

    def test_comment_on_next_line(self):
        """Test Comment: with summary on the following line."""
        lines = [
            "File: src/main.py",
            "Comment:",
            "The actual summary is here",
        ]
        metadata = parse_issue_metadata(lines)
        assert metadata["summary"] == "The actual summary is here"

    def test_long_summary_truncated(self):
        """Test that summaries longer than 60 chars are truncated."""
        long_text = "A" * 80
        lines = [
            f"Comment: {long_text}",
        ]
        metadata = parse_issue_metadata(lines)
        assert len(metadata["summary"]) == 60
        assert metadata["summary"].endswith("...")

    def test_no_prompt(self):
        """Test issue without prompt field."""
        lines = [
            "File: src/main.py",
            "Line: 10",
            "Comment: Some comment",
        ]
        metadata = parse_issue_metadata(lines)
        assert metadata["prompt"] == ""

    def test_prompt_field_in_parsed_issues(self):
        """Test that prompt is extracted when parsing full review output."""
        output = """File: src/main.py
Line: 10
Type: bug
Comment: Fix this
Prompt: Update the code to handle edge case
=====
File: src/other.py
Prompt: Another prompt here"""
        issues = parse_review_issues(output)
        assert len(issues) == 2
        assert issues[0].prompt == "Update the code to handle edge case"
        assert issues[1].prompt == "Another prompt here"
