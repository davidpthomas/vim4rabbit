"""Tests for vim4rabbit.cli module."""

from unittest.mock import patch

import pytest
from vim4rabbit.cli import (
    run_command,
    run_coderabbit,
    run_review,
)


class TestRunCommand:
    """Tests for run_command function."""

    def test_successful_command(self):
        """Test successful command execution."""
        output, exit_code = run_command(["echo", "hello"])
        assert exit_code == 0
        assert "hello" in output

    def test_failed_command(self):
        """Test failed command execution."""
        output, exit_code = run_command(["false"])
        assert exit_code != 0

    def test_command_not_found(self):
        """Test when command doesn't exist."""
        output, exit_code = run_command(["nonexistent_command_12345"])
        assert exit_code == 1
        assert "not found" in output.lower() or "nonexistent" in output.lower()

    def test_timeout(self):
        """Test command timeout."""
        # Use a very short timeout
        output, exit_code = run_command(["sleep", "10"], timeout=1)
        assert exit_code == 1
        assert "timed out" in output.lower()


class TestRunCoderabbit:
    """Tests for run_coderabbit function."""

    @patch("vim4rabbit.cli.run_command")
    def test_no_args(self, mock_run):
        """Test running coderabbit without args."""
        mock_run.return_value = ("output", 0)
        output, code = run_coderabbit()
        mock_run.assert_called_once_with(["coderabbit"], 60)

    @patch("vim4rabbit.cli.run_command")
    def test_with_args(self, mock_run):
        """Test running coderabbit with args."""
        mock_run.return_value = ("output", 0)
        output, code = run_coderabbit(["--plain", "--verbose"])
        mock_run.assert_called_once_with(["coderabbit", "--plain", "--verbose"], 60)


class TestRunReview:
    """Tests for run_review function."""

    @patch("vim4rabbit.cli.run_coderabbit")
    def test_successful_review(self, mock_run):
        """Test successful review execution."""
        mock_run.return_value = ("Issue 1\n=====\nIssue 2", 0)
        result = run_review()
        assert result.success is True
        assert len(result.issues) == 2
        mock_run.assert_called_once_with(["--plain"])

    @patch("vim4rabbit.cli.run_coderabbit")
    def test_failed_review(self, mock_run):
        """Test failed review execution."""
        mock_run.return_value = ("Error: not authenticated", 1)
        result = run_review()
        assert result.success is False
        assert "not authenticated" in result.error_message

    @patch("vim4rabbit.cli.run_coderabbit")
    def test_no_issues(self, mock_run):
        """Test review with no issues."""
        mock_run.return_value = ("", 0)
        result = run_review()
        assert result.success is True
        assert len(result.issues) == 0
