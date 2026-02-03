#!/usr/bin/env python3
"""
Timeline Generator - Generate chronological campaign timeline.

Aggregates events from sessions, NPCs, locations, and custom events.md
to produce a comprehensive campaign/timeline.md file.

Usage:
    python scripts/campaign/timeline_generator.py
    python scripts/campaign/timeline_generator.py --output timeline.md
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.campaign_calendar import InGameDate, format_in_game_date, parse_in_game_date
from lib.markdown_writer import bold, heading, horizontal_rule, iso_date


@dataclass
class TimelineEvent:
    """Represents a single event in the campaign timeline."""

    in_game_date: InGameDate
    title: str
    category: str
    description: str = ""
    real_date: str = ""
    session_number: Optional[int] = None
    entity_path: str = ""
    source: str = ""


def collect_session_events(sessions_dir: Path) -> list[TimelineEvent]:
    """Extract events from session files with in-game dates.

    Args:
        sessions_dir: Path to sessions directory

    Returns:
        List of TimelineEvents from sessions
    """
    events = []

    if not sessions_dir.exists():
        return events

    for session_file in sessions_dir.glob("session-*.md"):
        content = session_file.read_text(encoding="utf-8")

        # Extract session number
        match = re.search(r"session-(\d+)\.md", session_file.name)
        if not match:
            continue
        session_num = int(match.group(1))

        # Extract in-game date
        date_match = re.search(r"\*\*In-Game Date\*\*:\s*([Dd]ay\s*\d+)", content)
        if not date_match:
            continue  # Skip sessions without in-game dates

        in_game_date = parse_in_game_date(date_match.group(1))
        if not in_game_date:
            continue

        # Extract title from heading
        title_match = re.search(r"# Session \d+: (.+)", content)
        title = title_match.group(1) if title_match else f"Session {session_num}"

        # Extract real date
        real_date_match = re.search(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})", content)
        real_date = real_date_match.group(1) if real_date_match else ""

        # Extract summary if available (first paragraph after ## Summary)
        summary = ""
        summary_match = re.search(r"## Summary\s*\n+(.+?)(?=\n##|\n\*|$)", content, re.DOTALL)
        if summary_match:
            summary_text = summary_match.group(1).strip()
            # Take first paragraph, skip placeholders
            if not summary_text.startswith("*"):
                # Take first 200 chars or first paragraph
                summary = summary_text[:200]
                if len(summary_text) > 200:
                    summary += "..."

        events.append(TimelineEvent(
            in_game_date=in_game_date,
            title=f"Session {session_num}: {title}",
            category="session",
            description=summary,
            real_date=real_date,
            session_number=session_num,
            entity_path=f"sessions/{session_file.name}",
            source="session",
        ))

    return events


def collect_npc_events(npcs_dir: Path) -> list[TimelineEvent]:
    """Extract NPC first appearances.

    Args:
        npcs_dir: Path to NPCs directory

    Returns:
        List of TimelineEvents from NPC first appearances
    """
    events = []

    if not npcs_dir.exists():
        return events

    for npc_file in npcs_dir.glob("*.md"):
        if npc_file.name == "index.md":
            continue

        content = npc_file.read_text(encoding="utf-8")

        # Extract first appearance date
        date_match = re.search(r"\*\*First Appearance\*\*:\s*([Dd]ay\s*\d+)", content)
        if not date_match:
            continue  # Skip NPCs without first appearance dates

        in_game_date = parse_in_game_date(date_match.group(1))
        if not in_game_date:
            continue

        # Extract name from heading
        name_match = re.search(r"# (.+)", content)
        name = name_match.group(1) if name_match else npc_file.stem

        # Extract role
        role_match = re.search(r"\*\*Role\*\*:\s*(\w+)", content)
        role = role_match.group(1).lower() if role_match else "neutral"

        events.append(TimelineEvent(
            in_game_date=in_game_date,
            title=f"{name} first appears",
            category="npc",
            description=f"Role: {role.title()}",
            entity_path=f"npcs/{npc_file.name}",
            source="npc",
        ))

    return events


def collect_location_events(locations_dir: Path) -> list[TimelineEvent]:
    """Extract location discoveries.

    Args:
        locations_dir: Path to locations directory

    Returns:
        List of TimelineEvents from location discoveries
    """
    events = []

    if not locations_dir.exists():
        return events

    for location_file in locations_dir.glob("*.md"):
        if location_file.name == "index.md":
            continue

        content = location_file.read_text(encoding="utf-8")

        # Extract discovered date
        date_match = re.search(r"\*\*Discovered\*\*:\s*([Dd]ay\s*\d+)", content)
        if not date_match:
            continue  # Skip locations without discovery dates

        in_game_date = parse_in_game_date(date_match.group(1))
        if not in_game_date:
            continue

        # Extract name from heading
        name_match = re.search(r"# (.+)", content)
        name = name_match.group(1) if name_match else location_file.stem

        # Extract type
        type_match = re.search(r"\*\*Type\*\*:\s*(\w+)", content)
        loc_type = type_match.group(1).lower() if type_match else "other"

        events.append(TimelineEvent(
            in_game_date=in_game_date,
            title=f"{name} discovered",
            category="location",
            description=f"Type: {loc_type.title()}",
            entity_path=f"locations/{location_file.name}",
            source="location",
        ))

    return events


def collect_custom_events(events_path: Path) -> list[TimelineEvent]:
    """Parse events from events.md table.

    Args:
        events_path: Path to events.md file

    Returns:
        List of TimelineEvents from custom events
    """
    events = []

    if not events_path.exists():
        return events

    content = events_path.read_text(encoding="utf-8")

    # Parse markdown table
    # Format: | In-Game Date | Event | Session | Category |
    lines = content.split("\n")
    in_table = False

    for line in lines:
        line = line.strip()

        # Skip header row and separator
        if line.startswith("| In-Game Date") or line.startswith("| ---"):
            in_table = True
            continue

        if not in_table:
            continue

        # Stop at end of table
        if not line.startswith("|"):
            in_table = False
            continue

        # Parse table row
        parts = [p.strip() for p in line.split("|")[1:-1]]  # Remove empty first/last from split
        if len(parts) < 4:
            continue

        date_str, event_title, session_str, category = parts[:4]

        in_game_date = parse_in_game_date(date_str)
        if not in_game_date:
            continue

        # Parse session number if provided
        session_number = None
        if session_str.strip():
            try:
                session_number = int(session_str.strip())
            except ValueError:
                pass

        events.append(TimelineEvent(
            in_game_date=in_game_date,
            title=event_title,
            category=category.strip() or "custom",
            session_number=session_number,
            source="events.md",
        ))

    return events


def get_campaign_name(campaign_dir: Path) -> str:
    """Extract campaign name from campaign.md.

    Args:
        campaign_dir: Path to campaign directory

    Returns:
        Campaign name or default
    """
    campaign_file = campaign_dir / "campaign.md"
    if not campaign_file.exists():
        return "Campaign Timeline"

    content = campaign_file.read_text(encoding="utf-8")
    name_match = re.search(r"# (.+)", content)
    return name_match.group(1) if name_match else "Campaign Timeline"


def generate_timeline(campaign_dir: Path, output_path: Path) -> dict:
    """Aggregate all events, sort, and write timeline.md.

    Args:
        campaign_dir: Path to campaign directory
        output_path: Path to output file

    Returns:
        Statistics about the generated timeline
    """
    # Collect events from all sources
    all_events: list[TimelineEvent] = []

    session_events = collect_session_events(campaign_dir / "sessions")
    npc_events = collect_npc_events(campaign_dir / "npcs")
    location_events = collect_location_events(campaign_dir / "locations")
    custom_events = collect_custom_events(campaign_dir / "events.md")

    all_events.extend(session_events)
    all_events.extend(npc_events)
    all_events.extend(location_events)
    all_events.extend(custom_events)

    # Sort by in-game date
    all_events.sort(key=lambda e: e.in_game_date.day)

    # Get campaign info
    campaign_name = get_campaign_name(campaign_dir)
    current_day = max((e.in_game_date.day for e in all_events), default=0)
    session_count = len(session_events)

    # Generate markdown
    lines = [
        f"# {campaign_name} Timeline",
        "",
        f"{bold('Campaign')}: {campaign_name}  ",
        f"{bold('Current Day')}: Day {current_day}  " if current_day > 0 else "",
        f"{bold('Sessions')}: {session_count}  ",
        f"{bold('Generated')}: {iso_date()}",
        "",
        horizontal_rule(),
        "",
    ]

    if not all_events:
        lines.append("*No timeline events found. Add in-game dates to sessions, NPCs, or locations, or add custom events to events.md.*")
    else:
        # Group events by day
        current_day_num = None

        for event in all_events:
            if event.in_game_date.day != current_day_num:
                # New day section
                current_day_num = event.in_game_date.day
                lines.append(f"## {format_in_game_date(event.in_game_date)}")
                lines.append("")

                # Add real date if available from session
                if event.real_date and event.category == "session":
                    lines.append(f"*Real Date: {event.real_date}*")
                    lines.append("")

            # Format event based on category
            if event.category == "session":
                if event.entity_path:
                    lines.append(f"### [{event.title}]({event.entity_path})")
                else:
                    lines.append(f"### {event.title}")
                if event.description:
                    lines.append("")
                    lines.append(event.description)
            else:
                # NPC, location, or custom event as bullet
                icon = {
                    "npc": "👤",
                    "location": "📍",
                    "battle": "⚔️",
                    "plot": "📖",
                    "discovery": "🔍",
                    "start": "🎬",
                }.get(event.category, "•")

                if event.entity_path:
                    lines.append(f"- {icon} [{event.title}]({event.entity_path})")
                else:
                    lines.append(f"- {icon} {event.title}")

                if event.description:
                    lines.append(f"  - {event.description}")

            lines.append("")

    lines.append(horizontal_rule())
    lines.append("")
    lines.append(f"*Timeline generated on {iso_date()}*")

    # Write to file
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "total_events": len(all_events),
        "sessions": len(session_events),
        "npcs": len(npc_events),
        "locations": len(location_events),
        "custom": len(custom_events),
        "current_day": current_day,
    }


def find_repo_root() -> Path:
    """Find the repository root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "books").exists() or (current / "scripts").exists():
            return current
        current = current.parent
    return Path.cwd()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a chronological campaign timeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/timeline_generator.py
    python scripts/campaign/timeline_generator.py --output custom-timeline.md

The timeline includes:
    - Sessions with in-game dates
    - NPC first appearances
    - Location discoveries
    - Custom events from events.md
        """,
    )

    parser.add_argument(
        "--output", "-o",
        default="timeline.md",
        help="Output filename (default: timeline.md)",
    )

    args = parser.parse_args()

    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"

    if not campaign_dir.exists():
        print("Error: Campaign directory not found. Run init_campaign.py first.")
        sys.exit(1)

    output_path = campaign_dir / args.output

    print("Generating campaign timeline...")
    stats = generate_timeline(campaign_dir, output_path)

    print()
    print(f"Timeline: {output_path.relative_to(repo_root)}")
    print()
    print("Events collected:")
    print(f"  Sessions: {stats['sessions']}")
    print(f"  NPCs: {stats['npcs']}")
    print(f"  Locations: {stats['locations']}")
    print(f"  Custom events: {stats['custom']}")
    print(f"  Total: {stats['total_events']}")
    print()

    if stats['current_day'] > 0:
        print(f"Current in-game day: Day {stats['current_day']}")


if __name__ == "__main__":
    main()
