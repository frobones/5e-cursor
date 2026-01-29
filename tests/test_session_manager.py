"""Tests for session manager."""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.markdown_writer import session_filename


class TestSessionFilename:
    """Tests for session filename generation."""

    def test_single_digit(self):
        """Test single digit session number."""
        assert session_filename(1) == "session-001.md"
        assert session_filename(5) == "session-005.md"

    def test_double_digit(self):
        """Test double digit session number."""
        assert session_filename(10) == "session-010.md"
        assert session_filename(42) == "session-042.md"

    def test_triple_digit(self):
        """Test triple digit session number."""
        assert session_filename(100) == "session-100.md"
        assert session_filename(999) == "session-999.md"


class TestSessionNumberDetection:
    """Tests for next session number detection."""

    def test_empty_directory(self, tmp_path):
        """Test with no existing sessions."""
        from campaign.session_manager import get_next_session_number

        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        assert get_next_session_number(sessions_dir) == 1

    def test_with_existing_sessions(self, tmp_path):
        """Test with existing session files."""
        from campaign.session_manager import get_next_session_number

        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        (sessions_dir / "session-001.md").write_text("Session 1")
        (sessions_dir / "session-002.md").write_text("Session 2")
        (sessions_dir / "session-003.md").write_text("Session 3")

        assert get_next_session_number(sessions_dir) == 4

    def test_with_gaps(self, tmp_path):
        """Test with gaps in session numbers."""
        from campaign.session_manager import get_next_session_number

        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        (sessions_dir / "session-001.md").write_text("Session 1")
        (sessions_dir / "session-005.md").write_text("Session 5")

        # Should return next after highest, not fill gaps
        assert get_next_session_number(sessions_dir) == 6

    def test_nonexistent_directory(self, tmp_path):
        """Test with nonexistent directory."""
        from campaign.session_manager import get_next_session_number

        sessions_dir = tmp_path / "nonexistent"
        assert get_next_session_number(sessions_dir) == 1
