#!/usr/bin/env python3
"""
Initialize a new campaign directory structure.

Usage:
    python scripts/campaign/init_campaign.py "Campaign Name"
    python scripts/campaign/init_campaign.py  # Uses default name "My Campaign"
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import heading, bold, bullet_list, horizontal_rule, iso_date


def create_campaign_structure(campaign_name: str, base_dir: Path) -> None:
    """Create the campaign directory structure.

    Args:
        campaign_name: Name of the campaign
        base_dir: Base directory (usually repo root)
    """
    campaign_dir = base_dir / "campaign"

    # Create directories
    dirs = [
        campaign_dir,
        campaign_dir / "party" / "characters",
        campaign_dir / "npcs",
        campaign_dir / "locations",
        campaign_dir / "sessions",
        campaign_dir / "encounters",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"Created: {d.relative_to(base_dir)}")

    # Create campaign.md
    campaign_md = campaign_dir / "campaign.md"
    if not campaign_md.exists():
        content = f"""{heading(campaign_name)}

{bold("Created")}: {iso_date()}  
{bold("Setting")}: [Your setting here]  
{bold("Current Session")}: 0

## Overview

[Describe your campaign here]

## Themes

- [Theme 1]
- [Theme 2]

## House Rules

[Any house rules or modifications]

{horizontal_rule()}

*This file tracks overall campaign information. See subdirectories for party, NPCs, locations, sessions, and encounters.*
"""
        campaign_md.write_text(content, encoding="utf-8")
        print(f"Created: {campaign_md.relative_to(base_dir)}")

    # Create party index
    party_index = campaign_dir / "party" / "index.md"
    if not party_index.exists():
        content = f"""{heading("Party")}

{bold("Average Level")}: 1  
{bold("Party Size")}: 0

## Members

*No characters imported yet. Use `python scripts/campaign/import_character.py <url>` to import from D&D Beyond.*

## Notes

[Party composition notes, group dynamics, etc.]
"""
        party_index.write_text(content, encoding="utf-8")
        print(f"Created: {party_index.relative_to(base_dir)}")

    # Create NPC index
    npc_index = campaign_dir / "npcs" / "index.md"
    if not npc_index.exists():
        content = f"""{heading("NPCs")}

## Allies

*No NPCs added yet.*

## Neutral

*No NPCs added yet.*

## Enemies

*No NPCs added yet.*
"""
        npc_index.write_text(content, encoding="utf-8")
        print(f"Created: {npc_index.relative_to(base_dir)}")

    # Create locations index
    locations_index = campaign_dir / "locations" / "index.md"
    if not locations_index.exists():
        content = f"""{heading("Locations")}

*No locations added yet.*

## By Region

[Organize locations by region or type]
"""
        locations_index.write_text(content, encoding="utf-8")
        print(f"Created: {locations_index.relative_to(base_dir)}")

    # Create sessions index
    sessions_index = campaign_dir / "sessions" / "index.md"
    if not sessions_index.exists():
        content = f"""{heading("Session Log")}

| Session | Date | Title |
| ------- | ---- | ----- |

*No sessions recorded yet. Use `python scripts/campaign/session_manager.py new "Title"` to create a session.*
"""
        sessions_index.write_text(content, encoding="utf-8")
        print(f"Created: {sessions_index.relative_to(base_dir)}")

    # Create encounters index
    encounters_index = campaign_dir / "encounters" / "index.md"
    if not encounters_index.exists():
        content = f"""{heading("Saved Encounters")}

| Name | Difficulty | Party Level | Creatures |
| ---- | ---------- | ----------- | --------- |

*No encounters saved yet. Use `python scripts/campaign/encounter_builder.py --save "name"` to save an encounter.*
"""
        encounters_index.write_text(content, encoding="utf-8")
        print(f"Created: {encounters_index.relative_to(base_dir)}")

    print(f"\nCampaign '{campaign_name}' initialized at {campaign_dir.relative_to(base_dir)}/")


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
        description="Initialize a new campaign directory structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/init_campaign.py "Curse of Strahd"
    python scripts/campaign/init_campaign.py "My Homebrew Campaign"
    python scripts/campaign/init_campaign.py  # Uses "My Campaign"
        """,
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="My Campaign",
        help="Name of the campaign (default: 'My Campaign')",
    )

    args = parser.parse_args()

    base_dir = find_repo_root()
    create_campaign_structure(args.name, base_dir)


if __name__ == "__main__":
    main()
