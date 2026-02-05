"""Tests for vim4rabbit.content module."""

import pytest
from vim4rabbit.content import (
    render_help,
    format_review_output,
    format_loading_message,
    format_cancelled_message,
    get_no_work_animation_frame,
    get_no_work_frame_count,
    is_no_files_error,
    NO_WORK_ANIMATION_FRAMES,
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
        assert "[ru] Review Uncommitted" in full_text

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
        # Issues are displayed with checkbox format: [ ] 1. Issue
        assert "[ ] 1." in full_text
        assert "[ ] 2." in full_text
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
        assert "[q] close" in full_text


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


class TestNoWorkAnimation:
    """Tests for the no-work animation when there are no files to review."""

    def test_frame_count(self):
        """Test that we have the expected number of frames."""
        assert get_no_work_frame_count() == 8
        assert len(NO_WORK_ANIMATION_FRAMES) == 8

    def test_get_frame_wraps_around(self):
        """Test that frame index wraps around correctly."""
        frame_0 = get_no_work_animation_frame(0)
        frame_8 = get_no_work_animation_frame(8)  # Should wrap to 0
        # The frames should be the same
        assert frame_0 == frame_8

    def test_frame_content_structure(self):
        """Test that each frame has the expected structure."""
        for i in range(get_no_work_frame_count()):
            content = get_no_work_animation_frame(i)
            full_text = "\n".join(content)
            # Should have header
            assert "coderabbit" in full_text
            # Should have close instruction
            assert "[q] to close" in full_text
            # Should have the speech bubble content
            assert "No changes to review" in full_text
            assert "Looking for work" in full_text

    def test_frame_has_rabbit_ascii(self):
        """Test that frames contain rabbit ASCII art."""
        for i in range(get_no_work_frame_count()):
            content = get_no_work_animation_frame(i)
            full_text = "\n".join(content)
            # Should have rabbit ear ASCII
            assert r"(\__/)" in full_text or r"(\__/) " in full_text

    def test_speech_bubble_is_present(self):
        """Test that the speech bubble borders are present."""
        frame = get_no_work_animation_frame(0)
        full_text = "\n".join(frame)
        # Check for box drawing characters
        assert "╭" in full_text
        assert "╰" in full_text
        assert "╮" in full_text
        assert "╯" in full_text


class TestIsNoFilesError:
    """Tests for the is_no_files_error detection function."""

    def test_empty_message(self):
        """Test that empty message returns False."""
        assert is_no_files_error("") is False
        assert is_no_files_error(None) is False

    def test_detects_no_files(self):
        """Test detection of 'no files' messages."""
        assert is_no_files_error("No files to review") is True
        assert is_no_files_error("no files found") is True
        assert is_no_files_error("NO FILES IN DIFF") is True

    def test_detects_no_changes(self):
        """Test detection of 'no changes' messages."""
        assert is_no_files_error("No changes to review") is True
        assert is_no_files_error("no changes detected") is True

    def test_detects_nothing_to_review(self):
        """Test detection of 'nothing to review' messages."""
        assert is_no_files_error("Nothing to review here") is True
        assert is_no_files_error("There is nothing to review") is True

    def test_detects_no_diff(self):
        """Test detection of 'no diff' messages."""
        assert is_no_files_error("No diff available") is True
        assert is_no_files_error("no diff found") is True

    def test_detects_failed_to_start_review(self):
        """Test detection of 'failed to start review' messages."""
        assert is_no_files_error("Failed to start review") is True
        assert is_no_files_error("failed to start review: no files") is True

    def test_regular_errors_not_detected(self):
        """Test that regular errors are not detected as no-files errors."""
        assert is_no_files_error("Command not found: coderabbit") is False
        assert is_no_files_error("Permission denied") is False
        assert is_no_files_error("Network error") is False
        assert is_no_files_error("Syntax error in file.py") is False
