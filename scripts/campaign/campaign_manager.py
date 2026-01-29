#!/usr/bin/env python3
"""
Campaign Manager - Manage NPCs, locations, and campaign state.

Usage:
    python scripts/campaign/campaign_manager.py add-npc "Elara the Wise" --role ally --description "A sage..."
    python scripts/campaign/campaign_manager.py add-location "The Dragon's Rest Inn" --type tavern
    python scripts/campaign/campaign_manager.py list-npcs
    python scripts/campaign/campaign_manager.py list-locations
    python scripts/campaign/campaign_manager.py show-npc "Elara the Wise"
    python scripts/campaign/campaign_manager.py context
    python scripts/campaign/campaign_manager.py check-name "Elara"
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import bold, heading, horizontal_rule, iso_date, slugify


NPC_ROLES = ["ally", "neutral", "enemy", "unknown"]
ENTITY_TYPES = ["npc", "location"]
LOCATION_TYPES = ["city", "town", "village", "dungeon", "tavern", "shop", "temple", "wilderness", "landmark", "other"]


def create_npc(
    npcs_dir: Path,
    name: str,
    role: str = "neutral",
    description: str = "",
    occupation: str = "",
    location: str = "",
    personality: str = "",
    voice: str = "",
    secrets: str = "",
    combat: str = "",
    notes: str = "",
) -> Path:
    """Create a new NPC file.

    Args:
        npcs_dir: Path to NPCs directory
        name: NPC name
        role: Role (ally, neutral, enemy)
        description: Physical description
        occupation: Job or role in the world
        location: Where the NPC can be found
        personality: Personality traits, goals, motivations
        voice: Voice, mannerisms, speaking style
        secrets: Hidden information for DM reference
        combat: Combat role or stat block reference
        notes: Additional notes

    Returns:
        Path to created file
    """
    npcs_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{slugify(name)}.md"
    npc_path = npcs_dir / filename

    content = f"""{heading(name)}

{bold("Role")}: {role.title()}  
{bold("Occupation")}: {occupation or "Unknown"}  
{bold("Location")}: {location or "Unknown"}

{horizontal_rule()}

## Description

{description or "*Add physical description here...*"}

## Personality

{personality or "*Add personality traits, goals, and motivations here...*"}

**Voice/Mannerisms**: {voice or "*Describe speaking style, quirks, or memorable phrases...*"}

## Connections

*List relationships with other NPCs, factions, or the party...*

## Secrets

{secrets or "*Hidden information only the DM knows...*"}

## Combat

{combat or "*Non-combatant, or reference a stat block (e.g., use Veteran stats)...*"}

## Notes

{notes or "*Additional notes...*"}

{horizontal_rule()}

*Created on {iso_date()}*
"""

    npc_path.write_text(content, encoding="utf-8")
    return npc_path


def create_location(
    locations_dir: Path,
    name: str,
    location_type: str = "other",
    description: str = "",
    region: str = "",
    sights: str = "",
    sounds: str = "",
    smells: str = "",
    encounters: str = "",
    secrets: str = "",
    connections: Optional[list[str]] = None,
    notes: str = "",
) -> Path:
    """Create a new location file.

    Args:
        locations_dir: Path to locations directory
        name: Location name
        location_type: Type of location
        description: Description of the location
        region: Region or area the location is in
        sights: Visual details
        sounds: Audio details
        smells: Olfactory details
        encounters: Potential encounters or conflicts
        secrets: Hidden features or adventure hooks
        connections: Connected locations
        notes: Additional notes

    Returns:
        Path to created file
    """
    locations_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{slugify(name)}.md"
    location_path = locations_dir / filename

    connections_str = ""
    if connections:
        connections_str = "\n".join(f"- {c}" for c in connections)
    else:
        connections_str = "*No connections listed...*"

    content = f"""{heading(name)}

{bold("Type")}: {location_type.title()}  
{bold("Region")}: {region or "Unknown"}

{horizontal_rule()}

## Description

{description or "*Add description here...*"}

## Sensory Details

- **Sights**: {sights or "*What do visitors see?*"}
- **Sounds**: {sounds or "*What do visitors hear?*"}
- **Smells**: {smells or "*What do visitors smell?*"}

## Notable Features

*List interesting features, landmarks, or points of interest...*

## Key NPCs

*List NPCs found at this location...*

## Connections

{connections_str}

## Potential Encounters

{encounters or "*What conflicts or creatures might be encountered here?*"}

## Secrets

{secrets or "*Hidden features, adventure hooks, or DM-only information...*"}

## Notes

{notes or "*Additional notes...*"}

{horizontal_rule()}

*Created on {iso_date()}*
"""

    location_path.write_text(content, encoding="utf-8")
    return location_path


def update_npc_index(campaign_dir: Path, name: str, role: str, filename: str) -> None:
    """Update the NPC index with a new entry.

    Args:
        campaign_dir: Campaign directory
        name: NPC name
        role: NPC role
        filename: NPC filename
    """
    index_path = campaign_dir / "npcs" / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")

    # Check if already listed
    if filename in content:
        return

    # Find the appropriate section based on role
    section_map = {
        "ally": "## Allies",
        "neutral": "## Neutral",
        "enemy": "## Enemies",
        "unknown": "## Neutral",
    }
    target_section = section_map.get(role, "## Neutral")

    lines = content.split("\n")
    new_lines = []
    added = False

    for line in lines:
        new_lines.append(line)
        if line.strip() == target_section and not added:
            # Add NPC link after section header
            # Any placeholder lines will be removed below
            new_lines.append("")
            new_lines.append(f"- [{name}]({filename})")
            added = True

    # Remove placeholder lines
    final_lines = [l for l in new_lines if "*No NPCs added yet" not in l]

    index_path.write_text("\n".join(final_lines), encoding="utf-8")


def update_location_index(campaign_dir: Path, name: str, location_type: str, filename: str) -> None:
    """Update the location index with a new entry.

    Args:
        campaign_dir: Campaign directory
        name: Location name
        location_type: Location type
        filename: Location filename
    """
    index_path = campaign_dir / "locations" / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")

    # Check if already listed
    if filename in content:
        return

    lines = content.split("\n")
    new_lines = []

    for line in lines:
        if "*No locations added yet" in line:
            # Replace placeholder with entry
            new_lines.append(f"- [{name}]({filename}) ({location_type})")
        else:
            new_lines.append(line)
            # Add after the first heading if we haven't seen any entries
            if line.startswith("# ") and "*No locations added yet" not in content:
                # There might be existing locations, check if this is the header
                pass

    # If no placeholder was replaced, add at the end of locations list
    if f"[{name}]({filename})" not in "\n".join(new_lines):
        # Find insertion point (after main heading, before ## sections)
        insert_idx = 1
        for i, line in enumerate(new_lines):
            if line.startswith("## "):
                insert_idx = i
                break
            elif line.startswith("- ["):
                insert_idx = i + 1

        new_lines.insert(insert_idx, f"- [{name}]({filename}) ({location_type})")

    index_path.write_text("\n".join(new_lines), encoding="utf-8")


def list_npcs(npcs_dir: Path) -> list[dict]:
    """List all NPCs.

    Args:
        npcs_dir: Path to NPCs directory

    Returns:
        List of NPC info dicts
    """
    if not npcs_dir.exists():
        return []

    npcs = []

    for npc_file in sorted(npcs_dir.glob("*.md")):
        if npc_file.name == "index.md":
            continue

        content = npc_file.read_text(encoding="utf-8")

        # Extract name from heading
        name_match = re.search(r"# (.+)", content)
        name = name_match.group(1) if name_match else npc_file.stem

        # Extract role
        role_match = re.search(r"\*\*Role\*\*: (\w+)", content)
        role = role_match.group(1) if role_match else "Unknown"

        # Extract occupation
        occ_match = re.search(r"\*\*Occupation\*\*: (.+?)  ", content)
        occupation = occ_match.group(1) if occ_match else "Unknown"

        # Extract location
        loc_match = re.search(r"\*\*Location\*\*: (.+?)(?:\s*\n|$)", content)
        location = loc_match.group(1).strip() if loc_match else "Unknown"

        npcs.append({
            "name": name,
            "role": role,
            "occupation": occupation,
            "location": location,
            "filename": npc_file.name,
            "path": npc_file,
        })

    return npcs


def list_locations(locations_dir: Path) -> list[dict]:
    """List all locations.

    Args:
        locations_dir: Path to locations directory

    Returns:
        List of location info dicts
    """
    if not locations_dir.exists():
        return []

    locations = []

    for loc_file in sorted(locations_dir.glob("*.md")):
        if loc_file.name == "index.md":
            continue

        content = loc_file.read_text(encoding="utf-8")

        # Extract name from heading
        name_match = re.search(r"# (.+)", content)
        name = name_match.group(1) if name_match else loc_file.stem

        # Extract type
        type_match = re.search(r"\*\*Type\*\*: (\w+)", content)
        loc_type = type_match.group(1) if type_match else "Unknown"

        # Extract region
        region_match = re.search(r"\*\*Region\*\*: (.+?)  ", content)
        region = region_match.group(1) if region_match else "Unknown"

        locations.append({
            "name": name,
            "type": loc_type,
            "region": region,
            "filename": loc_file.name,
            "path": loc_file,
        })

    return locations


def get_campaign_overview(campaign_dir: Path) -> dict:
    """Extract campaign overview from campaign.md.

    Args:
        campaign_dir: Path to campaign directory

    Returns:
        Dict with campaign metadata
    """
    campaign_file = campaign_dir / "campaign.md"
    if not campaign_file.exists():
        return {"name": "Unknown", "setting": "", "themes": []}

    content = campaign_file.read_text(encoding="utf-8")

    # Extract name from heading
    name_match = re.search(r"# (.+)", content)
    name = name_match.group(1) if name_match else "Unknown"

    # Extract setting
    setting_match = re.search(r"\*\*Setting\*\*: (.+?)(?:\n|$)", content)
    setting = setting_match.group(1).strip() if setting_match else ""

    # Extract themes (look for a themes section or bullet list)
    themes = []
    themes_match = re.search(r"## Themes\s*\n((?:[-*] .+\n?)+)", content)
    if themes_match:
        themes = [line.strip("- *").strip() for line in themes_match.group(1).strip().split("\n")]

    return {
        "name": name,
        "setting": setting,
        "themes": themes,
    }


def get_recent_sessions(campaign_dir: Path, limit: int = 3) -> list[dict]:
    """Get the most recent sessions.

    Args:
        campaign_dir: Path to campaign directory
        limit: Maximum number of sessions to return

    Returns:
        List of recent session info dicts (newest first)
    """
    sessions_dir = campaign_dir / "sessions"
    if not sessions_dir.exists():
        return []

    sessions = []
    for session_file in sorted(sessions_dir.glob("session-*.md"), reverse=True):
        if len(sessions) >= limit:
            break

        content = session_file.read_text(encoding="utf-8")

        # Extract session number
        match = re.search(r"session-(\d+)\.md", session_file.name)
        if not match:
            continue

        session_num = int(match.group(1))

        # Extract title from heading
        title_match = re.search(r"# Session \d+: (.+)", content)
        title = title_match.group(1) if title_match else "Untitled"

        # Extract date
        date_match = re.search(r"\*\*Date\*\*: (\d{4}-\d{2}-\d{2})", content)
        session_date = date_match.group(1) if date_match else "Unknown"

        sessions.append({
            "number": session_num,
            "title": title,
            "date": session_date,
        })

    return sessions


def get_campaign_context(campaign_dir: Path) -> dict:
    """Get consolidated campaign context for AI consumption.

    Args:
        campaign_dir: Path to campaign directory

    Returns:
        Dict containing all campaign state
    """
    npcs_dir = campaign_dir / "npcs"
    locations_dir = campaign_dir / "locations"

    return {
        "campaign": get_campaign_overview(campaign_dir),
        "npcs": list_npcs(npcs_dir),
        "locations": list_locations(locations_dir),
        "recent_sessions": get_recent_sessions(campaign_dir),
    }


def format_campaign_context(context: dict) -> str:
    """Format campaign context as markdown for AI consumption.

    Args:
        context: Campaign context dict from get_campaign_context()

    Returns:
        Formatted markdown string
    """
    lines = []

    # Campaign overview
    campaign = context["campaign"]
    lines.append(f"# Campaign Context: {campaign['name']}")
    lines.append("")
    if campaign["setting"]:
        lines.append(f"**Setting**: {campaign['setting']}")
    if campaign["themes"]:
        lines.append(f"**Themes**: {', '.join(campaign['themes'])}")
    lines.append("")

    # NPCs
    npcs = context["npcs"]
    lines.append(f"## NPCs ({len(npcs)} total)")
    lines.append("")
    if npcs:
        lines.append("| Name | Role | Occupation | Location |")
        lines.append("| ---- | ---- | ---------- | -------- |")
        for npc in npcs:
            loc = npc.get("location", "Unknown")
            lines.append(f"| {npc['name']} | {npc['role']} | {npc['occupation']} | {loc} |")
    else:
        lines.append("*No NPCs created yet.*")
    lines.append("")

    # Locations
    locations = context["locations"]
    lines.append(f"## Locations ({len(locations)} total)")
    lines.append("")
    if locations:
        lines.append("| Name | Type | Region |")
        lines.append("| ---- | ---- | ------ |")
        for loc in locations:
            lines.append(f"| {loc['name']} | {loc['type']} | {loc['region']} |")
    else:
        lines.append("*No locations created yet.*")
    lines.append("")

    # Recent sessions
    sessions = context["recent_sessions"]
    lines.append(f"## Recent Sessions (last {len(sessions)})")
    lines.append("")
    if sessions:
        for session in sessions:
            lines.append(f"- **Session {session['number']}**: {session['title']} ({session['date']})")
    else:
        lines.append("*No sessions recorded yet.*")
    lines.append("")

    return "\n".join(lines)


def check_name_conflict(campaign_dir: Path, name: str, entity_type: Optional[str] = None) -> dict:
    """Check if a name conflicts with existing campaign entities.

    Args:
        campaign_dir: Path to campaign directory
        name: Name to check
        entity_type: Optional type to check ("npc", "location", or None for both)

    Returns:
        Dict with conflict info: {"has_conflict": bool, "conflicts": [...]}
    """
    conflicts = []
    name_lower = name.lower()
    name_slug = slugify(name)

    # Check NPCs
    if entity_type is None or entity_type == "npc":
        npcs_dir = campaign_dir / "npcs"
        for npc in list_npcs(npcs_dir):
            npc_name_lower = npc["name"].lower()
            npc_slug = slugify(npc["name"])

            # Check for exact match, case-insensitive match, or slug collision
            if (name_lower == npc_name_lower or name_slug == npc_slug):
                conflicts.append({
                    "type": "npc",
                    "name": npc["name"],
                    "file": npc["filename"],
                    "reason": "exact match" if name_lower == npc_name_lower else "slug collision",
                })

    # Check Locations
    if entity_type is None or entity_type == "location":
        locations_dir = campaign_dir / "locations"
        for loc in list_locations(locations_dir):
            loc_name_lower = loc["name"].lower()
            loc_slug = slugify(loc["name"])

            if (name_lower == loc_name_lower or name_slug == loc_slug):
                conflicts.append({
                    "type": "location",
                    "name": loc["name"],
                    "file": loc["filename"],
                    "reason": "exact match" if name_lower == loc_name_lower else "slug collision",
                })

    return {
        "has_conflict": len(conflicts) > 0,
        "conflicts": conflicts,
    }


def show_entity(entity_dir: Path, name: str) -> str:
    """Show content of an entity file.

    Args:
        entity_dir: Directory containing entities
        name: Entity name or filename

    Returns:
        Content or error message
    """
    # Try exact filename match
    filename = f"{slugify(name)}.md"
    entity_path = entity_dir / filename

    if entity_path.exists():
        return entity_path.read_text(encoding="utf-8")

    # Try searching by name
    for entity_file in entity_dir.glob("*.md"):
        if entity_file.name == "index.md":
            continue

        content = entity_file.read_text(encoding="utf-8")
        name_match = re.search(r"# (.+)", content)
        if name_match and name.lower() in name_match.group(1).lower():
            return content

    return f"Not found: {name}"


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
        description="Manage campaign NPCs and locations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/campaign_manager.py add-npc "Elara" --role ally --description "An elven sage"
    python scripts/campaign/campaign_manager.py add-location "Dragon's Rest" --type tavern
    python scripts/campaign/campaign_manager.py list-npcs
    python scripts/campaign/campaign_manager.py list-locations
    python scripts/campaign/campaign_manager.py show-npc "Elara"
    python scripts/campaign/campaign_manager.py show-location "Dragon's Rest"
    python scripts/campaign/campaign_manager.py context
    python scripts/campaign/campaign_manager.py check-name "Elara"
    python scripts/campaign/campaign_manager.py check-name "Dragon's Rest" --type location
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # add-npc command
    add_npc_parser = subparsers.add_parser("add-npc", help="Add a new NPC")
    add_npc_parser.add_argument("name", help="NPC name")
    add_npc_parser.add_argument("--role", "-r", choices=NPC_ROLES, default="neutral", help="NPC role")
    add_npc_parser.add_argument("--description", "-d", default="", help="Physical description")
    add_npc_parser.add_argument("--occupation", "-o", default="", help="Occupation")
    add_npc_parser.add_argument("--location", "-l", default="", help="Where the NPC can be found")
    add_npc_parser.add_argument("--personality", "-p", default="", help="Personality traits, goals, motivations")
    add_npc_parser.add_argument("--voice", "-v", default="", help="Voice, mannerisms, speaking style")
    add_npc_parser.add_argument("--secrets", "-s", default="", help="Hidden information for DM")
    add_npc_parser.add_argument("--combat", "-c", default="", help="Combat role or stat block reference")
    add_npc_parser.add_argument("--notes", "-n", default="", help="Additional notes")

    # add-location command
    add_loc_parser = subparsers.add_parser("add-location", help="Add a new location")
    add_loc_parser.add_argument("name", help="Location name")
    add_loc_parser.add_argument("--type", "-t", choices=LOCATION_TYPES, default="other", help="Location type")
    add_loc_parser.add_argument("--description", "-d", default="", help="Description")
    add_loc_parser.add_argument("--region", "-r", default="", help="Region or area")
    add_loc_parser.add_argument("--sights", default="", help="Visual details")
    add_loc_parser.add_argument("--sounds", default="", help="Audio details")
    add_loc_parser.add_argument("--smells", default="", help="Olfactory details")
    add_loc_parser.add_argument("--encounters", "-e", default="", help="Potential encounters")
    add_loc_parser.add_argument("--secrets", "-s", default="", help="Hidden features or hooks")
    add_loc_parser.add_argument("--notes", "-n", default="", help="Additional notes")

    # list-npcs command
    subparsers.add_parser("list-npcs", help="List all NPCs")

    # list-locations command
    subparsers.add_parser("list-locations", help="List all locations")

    # show-npc command
    show_npc_parser = subparsers.add_parser("show-npc", help="Show an NPC")
    show_npc_parser.add_argument("name", help="NPC name")

    # show-location command
    show_loc_parser = subparsers.add_parser("show-location", help="Show a location")
    show_loc_parser.add_argument("name", help="Location name")

    # context command
    subparsers.add_parser("context", help="Show campaign context summary for AI consumption")

    # check-name command
    check_name_parser = subparsers.add_parser("check-name", help="Check if a name conflicts with existing entities")
    check_name_parser.add_argument("name", help="Name to check")
    check_name_parser.add_argument(
        "--type", "-t",
        choices=ENTITY_TYPES,
        default=None,
        help="Entity type to check (npc, location, or omit for both)"
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"
    npcs_dir = campaign_dir / "npcs"
    locations_dir = campaign_dir / "locations"

    if not campaign_dir.exists():
        print("Error: Campaign directory not found. Run init_campaign.py first.")
        sys.exit(1)

    if args.command == "add-npc":
        npc_path = create_npc(
            npcs_dir,
            args.name,
            role=args.role,
            description=args.description,
            occupation=args.occupation,
            location=args.location,
            personality=args.personality,
            voice=args.voice,
            secrets=args.secrets,
            combat=args.combat,
            notes=args.notes,
        )
        update_npc_index(campaign_dir, args.name, args.role, npc_path.name)
        print(f"Created NPC: {args.name}")
        print(f"File: {npc_path}")

    elif args.command == "add-location":
        loc_path = create_location(
            locations_dir,
            args.name,
            location_type=args.type,
            description=args.description,
            region=args.region,
            sights=args.sights,
            sounds=args.sounds,
            smells=args.smells,
            encounters=args.encounters,
            secrets=args.secrets,
            notes=args.notes,
        )
        update_location_index(campaign_dir, args.name, args.type, loc_path.name)
        print(f"Created location: {args.name}")
        print(f"File: {loc_path}")

    elif args.command == "list-npcs":
        npcs = list_npcs(npcs_dir)

        if not npcs:
            print("No NPCs created yet.")
            return

        print(f"{'Name':<30} {'Role':<10} {'Occupation':<30}")
        print("-" * 70)

        for npc in npcs:
            print(f"{npc['name']:<30} {npc['role']:<10} {npc['occupation']:<30}")

        print(f"\nTotal: {len(npcs)} NPCs")

    elif args.command == "list-locations":
        locations = list_locations(locations_dir)

        if not locations:
            print("No locations created yet.")
            return

        print(f"{'Name':<30} {'Type':<15} {'Region':<25}")
        print("-" * 70)

        for loc in locations:
            print(f"{loc['name']:<30} {loc['type']:<15} {loc['region']:<25}")

        print(f"\nTotal: {len(locations)} locations")

    elif args.command == "show-npc":
        content = show_entity(npcs_dir, args.name)
        print(content)

    elif args.command == "show-location":
        content = show_entity(locations_dir, args.name)
        print(content)

    elif args.command == "context":
        context = get_campaign_context(campaign_dir)
        print(format_campaign_context(context))

    elif args.command == "check-name":
        result = check_name_conflict(campaign_dir, args.name, args.type)

        if result["has_conflict"]:
            print(f"Name '{args.name}' has conflicts:")
            for conflict in result["conflicts"]:
                print(f"  - {conflict['type'].upper()}: {conflict['name']} ({conflict['file']}) - {conflict['reason']}")
            sys.exit(1)
        else:
            print(f"Name '{args.name}' is available.")
            sys.exit(0)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
