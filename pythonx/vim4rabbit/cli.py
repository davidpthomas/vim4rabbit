"""
CLI execution for vim4rabbit.

This module handles subprocess execution of the CodeRabbit CLI.
"""

import subprocess
from typing import Tuple

from .parser import parse_review_issues
from .types import ReviewResult


def run_command(cmd: list, timeout: int = 60) -> Tuple[str, int]:
    """
    Run a shell command and return output and exit code.

    Args:
        cmd: Command and arguments as list
        timeout: Timeout in seconds (default 60)

    Returns:
        Tuple of (stdout+stderr output, exit code)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return output, result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out", 1
    except FileNotFoundError:
        return f"Command not found: {cmd[0]}", 1
    except Exception as e:
        return str(e), 1


def run_coderabbit(args: list = None, timeout: int = 60) -> Tuple[str, int]:
    """
    Run the coderabbit CLI with optional arguments.

    Args:
        args: Optional list of arguments to pass to coderabbit
        timeout: Timeout in seconds

    Returns:
        Tuple of (output, exit code)
    """
    cmd = ["coderabbit"]
    if args:
        cmd.extend(args)
    return run_command(cmd, timeout)


def run_review() -> ReviewResult:
    """
    Run CodeRabbit review and parse the output.

    Ported from vim4rabbit#RunReview() (CLI execution part).

    Returns:
        ReviewResult with success status, parsed issues, and any error message
    """
    output, exit_code = run_coderabbit(["--plain"])

    if exit_code != 0:
        return ReviewResult(
            success=False,
            error_message=output,
            raw_output=output,
        )

    issues = parse_review_issues(output)
    return ReviewResult(
        success=True,
        issues=issues,
        raw_output=output,
    )


def run_usage_json() -> Tuple[str, bool]:
    """
    Run 'coderabbit usage --json' command.

    Returns:
        Tuple of (output, success)
    """
    output, exit_code = run_coderabbit(["usage", "--json"])
    success = exit_code == 0 and output.strip()
    return output, success


def run_usage_plain() -> Tuple[str, bool]:
    """
    Run 'coderabbit usage' command (plain text).

    Returns:
        Tuple of (output, success)
    """
    output, exit_code = run_coderabbit(["usage"])
    success = exit_code == 0 and output.strip()
    return output, success
