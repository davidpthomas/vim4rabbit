"""Tests for vim4rabbit.content module."""

import pytest
from vim4rabbit.content import (
    render_help,
    format_review_output,
    format_loading_message,
    format_cancelled_message,
)
from vim4rabbit.types import ReviewResult, ReviewIssue


class TestRenderHelp:
    """Tests for render_help function."""

    def test_basic_structure(self):
        """Test basic help content structure."""
        content = render_help(80)
        assert len(content) >= 4  # Header, blank, commands, quit line
        assert "vim4rabbit Help" in content[0]

    def test_contains_review_command(self):
        """Test that help contains review command."""
        content = render_help(80)
        # Join all lines to search
        full_text = "\n".join(content)
        assert "[r] Review" in full_text

    def test_contains_quit_command(self):
        """Test that help contains quit command."""
        content = render_help(80)
        full_text = "\n".join(content)
        assert "[q] Quit" in full_text

    def test_width_affects_layout(self):
        """Test that different widths produce different layouts."""
        narrow = render_help(40)
        wide = render_help(120)
        # Quit line should be positioned differently
        narrow_quit = narrow[-1]
        wide_quit = wide[-1]
        # Wide version should have more padding
        assert len(wide_quit) > len(narrow_quit) or wide_quit.count(" ") > narrow_quit.count(" ")


class TestFormatReviewOutput:
    """Tests for format_review_output function."""

    def test_success_no_issues(self):
        """Test successful review with no issues."""
        result = ReviewResult(success=True, issues=[])
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "coderabbit" in full_text
        assert "No issues found" in full_text

    def test_success_with_issues(self):
        """Test successful review with issues."""
        issues = [
            ReviewIssue(lines=["Problem 1", "Details"]),
            ReviewIssue(lines=["Problem 2"]),
        ]
        result = ReviewResult(success=True, issues=issues)
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "Found 2 issue(s)" in full_text
        assert "Issue #1" in full_text
        assert "Issue #2" in full_text
        assert "Problem 1" in full_text
        assert "Problem 2" in full_text

    def test_error_result(self):
        """Test error result formatting."""
        result = ReviewResult(success=False, error_message="Command not found: coderabbit")
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "Error" in full_text
        assert "Command not found" in full_text

    def test_close_instruction(self):
        """Test that close instruction is present."""
        result = ReviewResult(success=True, issues=[])
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "[q] to close" in full_text


class TestFormatLoadingMessage:
    """Tests for format_loading_message function."""

    def test_loading_content(self):
        """Test loading message content."""
        content = format_loading_message()
        assert len(content) >= 3
        full_text = "\n".join(content)
        assert "coderabbit" in full_text
        assert "Running" in full_text

    def test_loading_shows_cancel_option(self):
        """Test that loading message shows cancel option."""
        content = format_loading_message()
        full_text = "\n".join(content)
        assert "[c] to cancel" in full_text


class TestFormatCancelledMessage:
    """Tests for format_cancelled_message function."""

    def test_cancelled_content(self):
        """Test cancelled message content."""
        content = format_cancelled_message()
        assert len(content) >= 3
        full_text = "\n".join(content)
        assert "coderabbit" in full_text
        assert "cancelled" in full_text.lower()

    def test_cancelled_shows_close_option(self):
        """Test that cancelled message shows close option."""
        content = format_cancelled_message()
        full_text = "\n".join(content)
        assert "[q] to close" in full_text
