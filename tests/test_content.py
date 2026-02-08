"""Tests for vim4rabbit.content module."""

import pytest
from vim4rabbit.content import (
    format_review_output,
    format_loading_message,
    format_cancelled_message,
    format_elapsed_time,
    get_animation_frame,
    get_no_work_animation_frame,
    get_no_work_frame_count,
    is_no_files_error,
    render_help,
    NO_WORK_ANIMATION_FRAMES,
)
from vim4rabbit.types import ReviewResult, ReviewIssue


class TestRenderHelp:
    """Tests for render_help function."""

    def test_help_contains_header(self):
        """Test that help screen contains the header."""
        content = render_help(80)
        full_text = "\n".join(content)
        assert "vim4rabbit Help" in full_text

    def test_help_contains_commands(self):
        """Test that help screen lists available commands."""
        content = render_help(80)
        full_text = "\n".join(content)
        assert "[ru]" in full_text
        assert "[rc]" in full_text
        assert "[ra]" in full_text
        assert "Review Uncommitted" in full_text
        assert "Review Committed" in full_text
        assert "Review All" in full_text

    def test_help_contains_quit(self):
        """Test that help screen shows quit option."""
        content = render_help(80)
        full_text = "\n".join(content)
        assert "[c] Close" in full_text

    def test_help_adapts_to_width(self):
        """Test that help screen adapts to different widths."""
        narrow = render_help(40)
        wide = render_help(120)
        # Both should have content
        assert len(narrow) > 0
        assert len(wide) > 0


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

    def test_fold_header_includes_issue_type(self):
        """Test that fold header includes issue type in brackets."""
        issues = [
            ReviewIssue(
                lines=["Details here"],
                issue_type="bug",
                summary="Null pointer dereference",
                file_path="src/main.py",
                line_range="10-20",
            ),
        ]
        result = ReviewResult(success=True, issues=issues)
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "[bug]" in full_text
        assert "Null pointer dereference" in full_text
        assert "(src/main.py:10-20)" in full_text

    def test_fold_header_defaults_issue_type(self):
        """Test that fold header defaults to 'issue' when type is empty."""
        issues = [
            ReviewIssue(lines=["Details"], summary="Some problem"),
        ]
        result = ReviewResult(success=True, issues=issues)
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "[issue]" in full_text
        assert "Some problem" in full_text

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
        assert "[c] close" in full_text


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
        assert "[c] cancel" in full_text


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
        assert "[c] to close" in full_text


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
            assert "[c] to close" in full_text
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


class TestFormatElapsedTime:
    """Tests for format_elapsed_time function."""

    def test_zero_seconds(self):
        """Test formatting zero seconds."""
        assert format_elapsed_time(0) == "00min 00sec"

    def test_seconds_only(self):
        """Test formatting with only seconds."""
        assert format_elapsed_time(5) == "00min 05sec"
        assert format_elapsed_time(41) == "00min 41sec"

    def test_minutes_and_seconds(self):
        """Test formatting with minutes and seconds."""
        assert format_elapsed_time(61) == "01min 01sec"
        assert format_elapsed_time(221) == "03min 41sec"

    def test_large_values(self):
        """Test formatting with large values."""
        assert format_elapsed_time(600) == "10min 00sec"
        assert format_elapsed_time(3599) == "59min 59sec"

    def test_exact_minute(self):
        """Test formatting exact minutes."""
        assert format_elapsed_time(60) == "01min 00sec"
        assert format_elapsed_time(120) == "02min 00sec"


class TestAnimationFrameElapsedTime:
    """Tests for elapsed time display in animation frames."""

    def test_animation_frame_shows_elapsed(self):
        """Test that animation frame includes elapsed time."""
        content = get_animation_frame(0, elapsed_secs=65)
        full_text = "\n".join(content)
        assert "01min 05sec" in full_text

    def test_animation_frame_shows_zero_elapsed(self):
        """Test that animation frame shows 00min 00sec at start."""
        content = get_animation_frame(0, elapsed_secs=0)
        full_text = "\n".join(content)
        assert "00min 00sec" in full_text

    def test_animation_frame_default_no_elapsed_arg(self):
        """Test that animation frame works without elapsed_secs arg."""
        content = get_animation_frame(0)
        full_text = "\n".join(content)
        assert "00min 00sec" in full_text


class TestFormatReviewOutputElapsedTime:
    """Tests for elapsed time display in review output."""

    def test_elapsed_time_shown_with_issues(self):
        """Test elapsed time is shown next to issue count."""
        issues = [ReviewIssue(lines=["Problem 1"])]
        result = ReviewResult(success=True, issues=issues)
        content = format_review_output(result, elapsed_secs=221)
        full_text = "\n".join(content)
        assert "Found 1 issue(s)" in full_text
        assert "03min 41sec" in full_text

    def test_elapsed_time_default_zero(self):
        """Test elapsed time defaults to zero."""
        issues = [ReviewIssue(lines=["Problem 1"])]
        result = ReviewResult(success=True, issues=issues)
        content = format_review_output(result)
        full_text = "\n".join(content)
        assert "00min 00sec" in full_text

    def test_no_elapsed_time_on_error(self):
        """Test that error results don't show elapsed time in issue line."""
        result = ReviewResult(success=False, error_message="Something failed")
        content = format_review_output(result, elapsed_secs=100)
        full_text = "\n".join(content)
        assert "Error" in full_text
        # Elapsed time should NOT appear in error output
        assert "01min 40sec" not in full_text

    def test_no_elapsed_time_when_no_issues(self):
        """Test that no-issues result doesn't show elapsed time."""
        result = ReviewResult(success=True, issues=[])
        content = format_review_output(result, elapsed_secs=100)
        full_text = "\n".join(content)
        assert "No issues found" in full_text
        assert "01min 40sec" not in full_text
