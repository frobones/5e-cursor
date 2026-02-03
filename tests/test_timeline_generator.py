"""Tests for timeline_generator.py"""

import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from campaign.timeline_generator import (
    TimelineEvent,
    collect_custom_events,
    collect_location_events,
    collect_npc_events,
    collect_session_events,
    generate_timeline,
    get_campaign_name,
)
from lib.campaign_calendar import InGameDate, format_in_game_date, parse_in_game_date


class TestInGameDate:
    """Tests for InGameDate parsing and formatting."""

    def test_parse_valid_date(self):
        """Test parsing valid date strings."""
        assert parse_in_game_date("Day 1") == InGameDate(day=1)
        assert parse_in_game_date("Day 15") == InGameDate(day=15)
        assert parse_in_game_date("Day 100") == InGameDate(day=100)

    def test_parse_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        assert parse_in_game_date("day 5") == InGameDate(day=5)
        assert parse_in_game_date("DAY 5") == InGameDate(day=5)
        assert parse_in_game_date("DaY 5") == InGameDate(day=5)

    def test_parse_flexible_whitespace(self):
        """Test that parsing handles various whitespace."""
        assert parse_in_game_date("Day15") == InGameDate(day=15)
        assert parse_in_game_date("Day  15") == InGameDate(day=15)
        assert parse_in_game_date("  Day 15  ") == InGameDate(day=15)

    def test_parse_invalid_date(self):
        """Test that invalid dates return None."""
        assert parse_in_game_date("") is None
        assert parse_in_game_date("invalid") is None
        assert parse_in_game_date("15 Day") is None
        assert parse_in_game_date("Day") is None
        assert parse_in_game_date("Day -5") is None

    def test_format_date(self):
        """Test formatting InGameDate to string."""
        assert format_in_game_date(InGameDate(day=1)) == "Day 1"
        assert format_in_game_date(InGameDate(day=15)) == "Day 15"
        assert format_in_game_date(InGameDate(day=100)) == "Day 100"

    def test_date_comparison(self):
        """Test that InGameDates can be compared."""
        day1 = InGameDate(day=1)
        day5 = InGameDate(day=5)
        day10 = InGameDate(day=10)

        assert day1 < day5
        assert day5 < day10
        assert day10 > day5
        assert day1 <= day1
        assert day5 >= day5

    def test_date_invalid_day(self):
        """Test that day must be positive."""
        with pytest.raises(ValueError):
            InGameDate(day=0)
        with pytest.raises(ValueError):
            InGameDate(day=-1)


class TestCollectSessionEvents:
    """Tests for collecting events from sessions."""

    def test_collect_from_session_with_date(self, tmp_path):
        """Test collecting events from a session with an in-game date."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        session_content = """# Session 1: The Beginning

**Date**: 2026-01-15  
**In-Game Date**: Day 1  
**Session Number**: 1

---

## Summary

The adventure begins in the village of Millbrook.
"""
        (sessions_dir / "session-001.md").write_text(session_content)

        events = collect_session_events(sessions_dir)

        assert len(events) == 1
        assert events[0].in_game_date.day == 1
        assert "Session 1" in events[0].title
        assert "The Beginning" in events[0].title
        assert events[0].category == "session"
        assert events[0].real_date == "2026-01-15"
        assert events[0].session_number == 1

    def test_skip_session_without_date(self, tmp_path):
        """Test that sessions without in-game dates are skipped."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        session_content = """# Session 1: The Beginning

**Date**: 2026-01-15  
**Session Number**: 1

---

## Summary

No in-game date here.
"""
        (sessions_dir / "session-001.md").write_text(session_content)

        events = collect_session_events(sessions_dir)

        assert len(events) == 0

    def test_collect_multiple_sessions(self, tmp_path):
        """Test collecting from multiple sessions."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        for i, (num, title, day) in enumerate([
            (1, "The Beginning", 1),
            (2, "Into the Caves", 5),
            (3, "The Final Battle", 10),
        ], 1):
            content = f"""# Session {num}: {title}

**Date**: 2026-01-{i:02d}  
**In-Game Date**: Day {day}  
**Session Number**: {num}

---
"""
            (sessions_dir / f"session-{num:03d}.md").write_text(content)

        events = collect_session_events(sessions_dir)

        assert len(events) == 3
        # Events are not sorted by the collector
        days = sorted(e.in_game_date.day for e in events)
        assert days == [1, 5, 10]


class TestCollectNPCEvents:
    """Tests for collecting NPC first appearance events."""

    def test_collect_npc_with_first_seen(self, tmp_path):
        """Test collecting NPC first appearance."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        npc_content = """# Grimbold the Blacksmith

**Role**: Neutral  
**Occupation**: Blacksmith  
**Location**: Millbrook  
**First Appearance**: Day 5  

---

## Description

A gruff but kind blacksmith.
"""
        (npcs_dir / "grimbold-the-blacksmith.md").write_text(npc_content)

        events = collect_npc_events(npcs_dir)

        assert len(events) == 1
        assert events[0].in_game_date.day == 5
        assert "Grimbold the Blacksmith" in events[0].title
        assert events[0].category == "npc"

    def test_skip_npc_without_first_seen(self, tmp_path):
        """Test that NPCs without first appearance are skipped."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        npc_content = """# Unknown NPC

**Role**: Enemy  
**Occupation**: Unknown  

---
"""
        (npcs_dir / "unknown-npc.md").write_text(npc_content)

        events = collect_npc_events(npcs_dir)

        assert len(events) == 0

    def test_skip_index_file(self, tmp_path):
        """Test that index.md is skipped."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        # Index shouldn't be parsed
        (npcs_dir / "index.md").write_text("# NPCs\n\n**First Appearance**: Day 1\n")

        events = collect_npc_events(npcs_dir)

        assert len(events) == 0


class TestCollectLocationEvents:
    """Tests for collecting location discovery events."""

    def test_collect_location_with_discovered(self, tmp_path):
        """Test collecting location discovery."""
        locations_dir = tmp_path / "locations"
        locations_dir.mkdir()

        location_content = """# Goblin Caves

**Type**: Dungeon  
**Region**: Northern Hills  
**Discovered**: Day 5  

---

## Description

Dark, damp caves.
"""
        (locations_dir / "goblin-caves.md").write_text(location_content)

        events = collect_location_events(locations_dir)

        assert len(events) == 1
        assert events[0].in_game_date.day == 5
        assert "Goblin Caves" in events[0].title
        assert events[0].category == "location"

    def test_skip_location_without_discovered(self, tmp_path):
        """Test that locations without discovery date are skipped."""
        locations_dir = tmp_path / "locations"
        locations_dir.mkdir()

        location_content = """# The Hidden Temple

**Type**: Temple  

---
"""
        (locations_dir / "hidden-temple.md").write_text(location_content)

        events = collect_location_events(locations_dir)

        assert len(events) == 0


class TestCollectCustomEvents:
    """Tests for collecting custom events from events.md."""

    def test_collect_custom_events(self, tmp_path):
        """Test parsing events from events.md table."""
        events_content = """# Campaign Events

| In-Game Date | Event | Session | Category |
| ------------ | ----- | ------- | -------- |
| Day 1 | Campaign begins | 1 | start |
| Day 5 | Defeated goblin chief | 2 | battle |
| Day 10 | Found the ancient artifact |  | discovery |

## Notes

More content here.
"""
        events_path = tmp_path / "events.md"
        events_path.write_text(events_content)

        events = collect_custom_events(events_path)

        assert len(events) == 3
        assert events[0].in_game_date.day == 1
        assert events[0].title == "Campaign begins"
        assert events[0].session_number == 1
        assert events[0].category == "start"

        assert events[1].in_game_date.day == 5
        assert events[1].title == "Defeated goblin chief"
        assert events[1].category == "battle"

        assert events[2].in_game_date.day == 10
        assert events[2].session_number is None  # Empty session

    def test_skip_invalid_rows(self, tmp_path):
        """Test that invalid rows are skipped."""
        events_content = """# Campaign Events

| In-Game Date | Event | Session | Category |
| ------------ | ----- | ------- | -------- |
| Day 1 | Valid event | 1 | start |
| Invalid | Bad date | 2 | battle |
| Day 5 | Another valid |  | plot |
"""
        events_path = tmp_path / "events.md"
        events_path.write_text(events_content)

        events = collect_custom_events(events_path)

        assert len(events) == 2
        assert events[0].in_game_date.day == 1
        assert events[1].in_game_date.day == 5

    def test_missing_events_file(self, tmp_path):
        """Test that missing events.md returns empty list."""
        events = collect_custom_events(tmp_path / "events.md")
        assert len(events) == 0


class TestGenerateTimeline:
    """Tests for full timeline generation."""

    def test_generate_full_timeline(self, tmp_path):
        """Test generating a complete timeline."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()

        # Create campaign.md
        (campaign_dir / "campaign.md").write_text("# Test Campaign\n")

        # Create session
        sessions_dir = campaign_dir / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "session-001.md").write_text("""# Session 1: Beginning

**Date**: 2026-01-15  
**In-Game Date**: Day 1  
**Session Number**: 1

---

## Summary

The adventure begins.
""")

        # Create NPC
        npcs_dir = campaign_dir / "npcs"
        npcs_dir.mkdir()
        (npcs_dir / "test-npc.md").write_text("""# Test NPC

**Role**: Ally  
**First Appearance**: Day 1  

---
""")

        # Create location
        locations_dir = campaign_dir / "locations"
        locations_dir.mkdir()
        (locations_dir / "test-location.md").write_text("""# Test Location

**Type**: Town  
**Discovered**: Day 1  

---
""")

        # Create events.md
        (campaign_dir / "events.md").write_text("""# Events

| In-Game Date | Event | Session | Category |
| ------------ | ----- | ------- | -------- |
| Day 1 | Campaign begins | 1 | start |
""")

        output_path = campaign_dir / "timeline.md"
        stats = generate_timeline(campaign_dir, output_path)

        assert output_path.exists()
        assert stats["sessions"] == 1
        assert stats["npcs"] == 1
        assert stats["locations"] == 1
        assert stats["custom"] == 1
        assert stats["total_events"] == 4
        assert stats["current_day"] == 1

        content = output_path.read_text()
        assert "Test Campaign" in content
        assert "Day 1" in content
        assert "Session 1" in content
        assert "Test NPC" in content
        assert "Test Location" in content

    def test_generate_empty_timeline(self, tmp_path):
        """Test generating timeline with no events."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()

        output_path = campaign_dir / "timeline.md"
        stats = generate_timeline(campaign_dir, output_path)

        assert output_path.exists()
        assert stats["total_events"] == 0

        content = output_path.read_text()
        assert "No timeline events found" in content

    def test_events_sorted_by_day(self, tmp_path):
        """Test that events are sorted by in-game date."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()

        # Create sessions in non-chronological order
        sessions_dir = campaign_dir / "sessions"
        sessions_dir.mkdir()

        for num, day in [(1, 10), (2, 1), (3, 5)]:
            (sessions_dir / f"session-{num:03d}.md").write_text(f"""# Session {num}: Test

**Date**: 2026-01-01  
**In-Game Date**: Day {day}  
**Session Number**: {num}

---
""")

        output_path = campaign_dir / "timeline.md"
        generate_timeline(campaign_dir, output_path)

        content = output_path.read_text()

        # Check that Day 1 appears before Day 5, and Day 5 before Day 10
        pos_day1 = content.find("## Day 1")
        pos_day5 = content.find("## Day 5")
        pos_day10 = content.find("## Day 10")

        assert pos_day1 < pos_day5 < pos_day10


class TestGetCampaignName:
    """Tests for extracting campaign name."""

    def test_get_campaign_name(self, tmp_path):
        """Test extracting campaign name from campaign.md."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()
        (campaign_dir / "campaign.md").write_text("# My Epic Campaign\n\nContent...")

        name = get_campaign_name(campaign_dir)
        assert name == "My Epic Campaign"

    def test_default_name_when_missing(self, tmp_path):
        """Test default name when campaign.md doesn't exist."""
        name = get_campaign_name(tmp_path)
        assert name == "Campaign Timeline"
