#!/usr/bin/env python3
"""
Campaign Manager - Manage NPCs, locations, and campaign state.

Usage:
    python scripts/campaign/campaign_manager.py add-npc "Elara the Wise" --role ally --description "A sage..."
    python scripts/campaign/campaign_manager.py add-location "The Dragon's Rest Inn" --type tavern
    python scripts/campaign/campaign_manager.py list-npcs
    python scripts/campaign/campaign_manager.py list-locations
    python scripts/campaign/campaign_manager.py show-npc "Elara the Wise"
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
LOCATION_TYPES = ["city", "town", "village", "dungeon", "tavern", "shop", "temple", "wilderness", "landmark", "other"]


def create_npc(
    npcs_dir: Path,
    name: str,
    role: str = "neutral",
    description: str = "",
    occupation: str = "",
    location: str = "",
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

*Add personality traits, mannerisms, goals, and secrets here...*

## Connections

*List relationships with other NPCs, factions, or the party...*

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

## Notable Features

*List interesting features, landmarks, or points of interest...*

## Key NPCs

*List NPCs found at this location...*

## Connections

{connections_str}

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

        npcs.append({
            "name": name,
            "role": role,
            "occupation": occupation,
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
    add_npc_parser.add_argument("--notes", "-n", default="", help="Additional notes")

    # add-location command
    add_loc_parser = subparsers.add_parser("add-location", help="Add a new location")
    add_loc_parser.add_argument("name", help="Location name")
    add_loc_parser.add_argument("--type", "-t", choices=LOCATION_TYPES, default="other", help="Location type")
    add_loc_parser.add_argument("--description", "-d", default="", help="Description")
    add_loc_parser.add_argument("--region", "-r", default="", help="Region or area")
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

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
