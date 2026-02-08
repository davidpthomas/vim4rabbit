"""Tests for vim4rabbit.__init__ module functions."""

import pytest
from vim4rabbit import (
    vim_build_claude_prompt,
    vim_format_review,
    vim_init_selections,
    vim_reset_selections,
    vim_toggle_selection,
    vim_select_all,
    vim_deselect_all,
    vim_get_selected,
    vim_get_issue_count,
    vim_find_issue_at_line,
)
from vim4rabbit import selection


class TestVimBuildClaudePrompt:
    """Tests for vim_build_claude_prompt function."""

    def test_empty_inputs(self):
        """Test with empty inputs."""
        assert vim_build_claude_prompt([], []) == ""
        assert vim_build_claude_prompt([1], []) == ""
        assert vim_build_claude_prompt([], [{"prompt": "test"}]) == ""

    def test_single_issue_with_prompt(self):
        """Test single issue with prompt."""
        issues = [
            {
                "file_path": "src/main.py",
                "line_range": "10-20",
                "summary": "Fix the bug",
                "prompt": "Update the function to handle null values",
            }
        ]
        result = vim_build_claude_prompt([1], issues)
        assert result == "Update the function to handle null values"

    def test_single_issue_fallback_without_prompt(self):
        """Test single issue without prompt uses fallback."""
        issues = [
            {
                "file_path": "src/main.py",
                "line_range": "10-20",
                "summary": "Fix the bug",
                "prompt": "",
            }
        ]
        result = vim_build_claude_prompt([1], issues)
        assert "src/main.py:10-20" in result
        assert "Fix the bug" in result

    def test_multiple_issues(self):
        """Test multiple selected issues."""
        issues = [
            {"prompt": "First fix", "file_path": "", "line_range": "", "summary": ""},
            {"prompt": "Second fix", "file_path": "", "line_range": "", "summary": ""},
            {"prompt": "Third fix", "file_path": "", "line_range": "", "summary": ""},
        ]
        result = vim_build_claude_prompt([1, 3], issues)
        assert "Issue 1" in result
        assert "First fix" in result
        assert "Issue 2" in result
        assert "Third fix" in result
        assert "Second fix" not in result

    def test_index_out_of_range(self):
        """Test that out-of-range indices are ignored."""
        issues = [
            {"prompt": "Valid fix", "file_path": "", "line_range": "", "summary": ""},
        ]
        result = vim_build_claude_prompt([1, 5, 10], issues)
        assert "Valid fix" in result

    def test_zero_index_ignored(self):
        """Test that zero index (invalid 1-based) is ignored."""
        issues = [
            {"prompt": "First fix", "file_path": "", "line_range": "", "summary": ""},
        ]
        result = vim_build_claude_prompt([0, 1], issues)
        assert "First fix" in result

    def test_combines_prompts_with_headers(self):
        """Test that multiple prompts are combined with issue headers."""
        issues = [
            {"prompt": "Fix A", "file_path": "", "line_range": "", "summary": ""},
            {"prompt": "Fix B", "file_path": "", "line_range": "", "summary": ""},
        ]
        result = vim_build_claude_prompt([1, 2], issues)
        assert "## Issue 1" in result
        assert "## Issue 2" in result
        assert "Fix A" in result
        assert "Fix B" in result


@pytest.fixture(autouse=True)
def clean_selection_state():
    """Reset selection state before each test."""
    selection.reset_selections()
    yield
    selection.reset_selections()


class TestVimFormatReview:
    """Tests for vim_format_review returning dict."""

    def test_returns_dict_with_lines_and_count(self):
        """Test that vim_format_review returns dict with lines and issue_count."""
        issues = [
            {"lines": ["Problem"], "file_path": "f.py", "line_range": "",
             "issue_type": "bug", "summary": "A bug", "prompt": ""},
        ]
        result = vim_format_review(True, issues, "")
        assert isinstance(result, dict)
        assert "lines" in result
        assert "issue_count" in result
        assert result["issue_count"] == 1
        assert isinstance(result["lines"], list)

    def test_error_returns_zero_issue_count(self):
        """Test that error results have issue_count 0."""
        result = vim_format_review(False, [], "Some error")
        assert result["issue_count"] == 0

    def test_backward_compat_plain_lines(self):
        """Test backward compatibility with plain list of lines."""
        issues = [["line1", "line2"]]
        result = vim_format_review(True, issues, "")
        assert result["issue_count"] == 1


class TestVimSelectionApi:
    """Tests for vim_* selection wrapper functions."""

    def test_init_and_get_count(self):
        """Test vim_init_selections and vim_get_issue_count."""
        vim_init_selections(5)
        assert vim_get_issue_count() == 5

    def test_reset(self):
        """Test vim_reset_selections."""
        vim_init_selections(5)
        vim_toggle_selection(1)
        vim_reset_selections()
        assert vim_get_issue_count() == 0
        assert vim_get_selected() == []

    def test_toggle(self):
        """Test vim_toggle_selection."""
        vim_init_selections(3)
        assert vim_toggle_selection(1) is True
        assert vim_toggle_selection(1) is False

    def test_select_all(self):
        """Test vim_select_all."""
        vim_init_selections(3)
        count = vim_select_all()
        assert count == 3
        assert vim_get_selected() == [1, 2, 3]

    def test_deselect_all(self):
        """Test vim_deselect_all."""
        vim_init_selections(3)
        vim_select_all()
        count = vim_deselect_all()
        assert count == 3
        assert vim_get_selected() == []

    def test_get_selected(self):
        """Test vim_get_selected returns sorted list."""
        vim_init_selections(5)
        vim_toggle_selection(3)
        vim_toggle_selection(1)
        assert vim_get_selected() == [1, 3]

    def test_find_issue_at_line(self):
        """Test vim_find_issue_at_line."""
        lines = [
            "  [ ] 1. [bug] Some bug {{{",
            "    details",
            "  }}}",
        ]
        assert vim_find_issue_at_line(lines, 0) == 1
        assert vim_find_issue_at_line(lines, 1) == 1

    def test_find_issue_at_line_not_found(self):
        """Test vim_find_issue_at_line returns 0 when not found."""
        lines = ["  header", "  footer"]
        assert vim_find_issue_at_line(lines, 0) == 0
