"""Tests for vim4rabbit.cache module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from vim4rabbit.cache import (
    get_cache_dir,
    get_cache_file,
    load_token_usage,
    save_token_cache,
    get_coderabbit_usage_file,
)
from vim4rabbit.types import TokenUsage


class TestCachePaths:
    """Tests for cache path functions."""

    def test_get_cache_dir(self):
        """Test cache directory path."""
        cache_dir = get_cache_dir()
        assert cache_dir == Path.home() / ".vim4rabbit"

    def test_get_cache_file(self):
        """Test cache file path."""
        cache_file = get_cache_file()
        assert cache_file == Path.home() / ".vim4rabbit" / "usage.json"


class TestLoadTokenUsage:
    """Tests for load_token_usage function."""

    def test_load_valid_cache(self, tmp_path):
        """Test loading valid cache file."""
        cache_dir = tmp_path / ".vim4rabbit"
        cache_dir.mkdir()
        cache_file = cache_dir / "usage.json"
        cache_file.write_text('{"used": 5000, "limit": 10000, "provider": "test"}')

        with patch("vim4rabbit.cache.get_cache_file", return_value=cache_file):
            usage = load_token_usage()
            assert usage is not None
            assert usage.used == 5000
            assert usage.limit == 10000
            assert usage.provider == "test"

    def test_load_missing_file(self, tmp_path):
        """Test loading when cache file doesn't exist."""
        cache_file = tmp_path / "nonexistent.json"

        with patch("vim4rabbit.cache.get_cache_file", return_value=cache_file):
            usage = load_token_usage()
            assert usage is None

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON."""
        cache_dir = tmp_path / ".vim4rabbit"
        cache_dir.mkdir()
        cache_file = cache_dir / "usage.json"
        cache_file.write_text("not valid json")

        with patch("vim4rabbit.cache.get_cache_file", return_value=cache_file):
            usage = load_token_usage()
            assert usage is None


class TestSaveTokenCache:
    """Tests for save_token_cache function."""

    def test_save_creates_directory(self, tmp_path):
        """Test that save creates directory if needed."""
        cache_dir = tmp_path / ".vim4rabbit"
        cache_file = cache_dir / "usage.json"

        with patch("vim4rabbit.cache.get_cache_dir", return_value=cache_dir):
            with patch("vim4rabbit.cache.get_cache_file", return_value=cache_file):
                usage = TokenUsage(used=1000, limit=5000, provider="test")
                result = save_token_cache(usage)

                assert result is True
                assert cache_dir.exists()
                assert cache_file.exists()

                data = json.loads(cache_file.read_text())
                assert data["used"] == 1000
                assert data["limit"] == 5000
                assert data["provider"] == "test"

    def test_save_overwrites_existing(self, tmp_path):
        """Test that save overwrites existing file."""
        cache_dir = tmp_path / ".vim4rabbit"
        cache_dir.mkdir()
        cache_file = cache_dir / "usage.json"
        cache_file.write_text('{"used": 100, "limit": 200, "provider": "old"}')

        with patch("vim4rabbit.cache.get_cache_dir", return_value=cache_dir):
            with patch("vim4rabbit.cache.get_cache_file", return_value=cache_file):
                usage = TokenUsage(used=9000, limit=10000, provider="new")
                result = save_token_cache(usage)

                assert result is True
                data = json.loads(cache_file.read_text())
                assert data["used"] == 9000
                assert data["provider"] == "new"


class TestGetCoderabbitUsageFile:
    """Tests for get_coderabbit_usage_file function."""

    def test_file_exists(self, tmp_path):
        """Test when CodeRabbit usage file exists."""
        cr_config = tmp_path / ".config" / "coderabbit"
        cr_config.mkdir(parents=True)
        cr_file = cr_config / "usage.json"
        cr_file.write_text("{}")

        with patch.object(Path, "home", return_value=tmp_path):
            result = get_coderabbit_usage_file()
            assert result == cr_file

    def test_file_not_exists(self, tmp_path):
        """Test when CodeRabbit usage file doesn't exist."""
        with patch.object(Path, "home", return_value=tmp_path):
            result = get_coderabbit_usage_file()
            assert result is None
