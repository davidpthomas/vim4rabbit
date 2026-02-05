"""Tests for vim4rabbit.__init__ module functions."""

import pytest
from vim4rabbit import vim_build_claude_prompt


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
