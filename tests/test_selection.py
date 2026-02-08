"""Tests for vim4rabbit.selection module."""

import pytest
from vim4rabbit import selection


@pytest.fixture(autouse=True)
def clean_state():
    """Reset selection state before each test."""
    selection.reset_selections()
    yield
    selection.reset_selections()


class TestInitSelections:
    """Tests for init_selections function."""

    def test_sets_issue_count(self):
        """Test that init_selections sets the issue count."""
        selection.init_selections(5)
        assert selection.get_issue_count() == 5

    def test_clears_previous_selections(self):
        """Test that init_selections clears any previous selections."""
        selection.init_selections(3)
        selection.toggle_selection(1)
        selection.toggle_selection(2)
        selection.init_selections(5)
        assert selection.get_selected() == []
        assert selection.get_issue_count() == 5


class TestResetSelections:
    """Tests for reset_selections function."""

    def test_clears_all_state(self):
        """Test that reset_selections clears everything."""
        selection.init_selections(3)
        selection.toggle_selection(1)
        selection.reset_selections()
        assert selection.get_selected() == []
        assert selection.get_issue_count() == 0


class TestToggleSelection:
    """Tests for toggle_selection function."""

    def test_toggle_on(self):
        """Test toggling a selection on."""
        selection.init_selections(3)
        result = selection.toggle_selection(1)
        assert result is True
        assert selection.get_selected() == [1]

    def test_toggle_off(self):
        """Test toggling a selection off."""
        selection.init_selections(3)
        selection.toggle_selection(1)
        result = selection.toggle_selection(1)
        assert result is False
        assert selection.get_selected() == []

    def test_toggle_multiple(self):
        """Test toggling multiple selections."""
        selection.init_selections(5)
        selection.toggle_selection(1)
        selection.toggle_selection(3)
        selection.toggle_selection(5)
        assert selection.get_selected() == [1, 3, 5]


class TestSelectAll:
    """Tests for select_all function."""

    def test_selects_all(self):
        """Test selecting all issues."""
        selection.init_selections(3)
        count = selection.select_all()
        assert count == 3
        assert selection.get_selected() == [1, 2, 3]

    def test_select_all_zero_issues(self):
        """Test selecting all when there are no issues."""
        selection.init_selections(0)
        count = selection.select_all()
        assert count == 0
        assert selection.get_selected() == []

    def test_select_all_overwrites_partial(self):
        """Test that select_all overwrites partial selections."""
        selection.init_selections(3)
        selection.toggle_selection(2)
        selection.select_all()
        assert selection.get_selected() == [1, 2, 3]


class TestDeselectAll:
    """Tests for deselect_all function."""

    def test_deselects_all(self):
        """Test deselecting all issues."""
        selection.init_selections(3)
        selection.select_all()
        count = selection.deselect_all()
        assert count == 3
        assert selection.get_selected() == []

    def test_deselect_all_when_none_selected(self):
        """Test deselecting when nothing is selected."""
        selection.init_selections(3)
        count = selection.deselect_all()
        assert count == 0
        assert selection.get_selected() == []


class TestGetSelected:
    """Tests for get_selected function."""

    def test_returns_sorted_list(self):
        """Test that get_selected returns a sorted list."""
        selection.init_selections(5)
        selection.toggle_selection(5)
        selection.toggle_selection(1)
        selection.toggle_selection(3)
        assert selection.get_selected() == [1, 3, 5]

    def test_empty_when_no_selections(self):
        """Test that get_selected returns empty list when nothing selected."""
        selection.init_selections(3)
        assert selection.get_selected() == []


class TestGetIssueCount:
    """Tests for get_issue_count function."""

    def test_returns_count(self):
        """Test that get_issue_count returns the issue count."""
        selection.init_selections(7)
        assert selection.get_issue_count() == 7

    def test_zero_after_reset(self):
        """Test that get_issue_count returns 0 after reset."""
        selection.init_selections(7)
        selection.reset_selections()
        assert selection.get_issue_count() == 0


class TestFindIssueAtLine:
    """Tests for find_issue_at_line function."""

    def test_finds_issue_on_fold_header(self):
        """Test finding issue when cursor is on fold header line."""
        lines = [
            "  header line",
            "  [ ] 1. [bug] Some bug (file.py:10) {{{",
            "    details here",
            "  }}}",
        ]
        assert selection.find_issue_at_line(lines, 1) == 1

    def test_finds_issue_inside_fold(self):
        """Test finding issue when cursor is inside fold body."""
        lines = [
            "  [ ] 1. [bug] Some bug (file.py:10) {{{",
            "    details here",
            "    more details",
            "  }}}",
        ]
        assert selection.find_issue_at_line(lines, 2) == 1

    def test_does_not_cross_fold_boundary(self):
        """Test that search stops at fold end marker."""
        lines = [
            "  [ ] 1. [bug] First issue {{{",
            "    details",
            "  }}}",
            "",
            "  some line between folds",
        ]
        assert selection.find_issue_at_line(lines, 4) == 0

    def test_finds_second_issue(self):
        """Test finding the second issue."""
        lines = [
            "  [ ] 1. [bug] First {{{",
            "    details",
            "  }}}",
            "",
            "  [ ] 2. [style] Second {{{",
            "    details",
            "  }}}",
        ]
        assert selection.find_issue_at_line(lines, 4) == 2
        assert selection.find_issue_at_line(lines, 5) == 2

    def test_returns_zero_for_empty_lines(self):
        """Test that empty lines list returns 0."""
        assert selection.find_issue_at_line([], 0) == 0

    def test_returns_zero_for_invalid_index(self):
        """Test that invalid cursor index returns 0."""
        lines = ["  [ ] 1. [bug] Issue {{{"]
        assert selection.find_issue_at_line(lines, -1) == 0
        assert selection.find_issue_at_line(lines, 5) == 0

    def test_returns_zero_for_non_issue_area(self):
        """Test that non-issue area returns 0."""
        lines = [
            "  header",
            "  some text",
            "  footer",
        ]
        assert selection.find_issue_at_line(lines, 1) == 0

    def test_finds_selected_issue(self):
        """Test finding issue with [x] checkbox."""
        lines = [
            "  [x] 3. [perf] Performance issue {{{",
            "    details",
            "  }}}",
        ]
        assert selection.find_issue_at_line(lines, 0) == 3
        assert selection.find_issue_at_line(lines, 1) == 3
