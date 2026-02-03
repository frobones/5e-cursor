"""
Relationship Parser - Parse NPC relationships from markdown files.

Parses the structured relationship format from NPC Connections sections.

Format:
    - [Name](file.md) | type | description
    - Name | type | description

Usage:
    from lib.relationship_parser import parse_connections_from_file, Relationship

    relationships = parse_connections_from_file(Path("campaign/npcs/elara.md"))
    for rel in relationships:
        print(f"{rel.target_name}: {rel.relationship_type}")
"""

import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Valid relationship types and their inverses
RELATIONSHIP_TYPES = {
    "ally": "ally",
    "enemy": "enemy",
    "family": "family",
    "employer": "employee",
    "employee": "employer",
    "rival": "rival",
    "neutral": "neutral",
    "romantic": "romantic",
    "mentor": "student",
    "student": "mentor",
}


@dataclass
class Relationship:
    """Represents a relationship between two NPCs.

    Attributes:
        source_name: Name of the source NPC
        source_file: Filename of source NPC (if known)
        target_name: Name of the target NPC
        target_file: Filename of target NPC (if linked)
        relationship_type: Type of relationship
        description: Freeform description of the relationship
    """

    source_name: str
    source_file: Optional[str]
    target_name: str
    target_file: Optional[str]
    relationship_type: str
    description: str = ""

    def get_inverse_type(self) -> str:
        """Get the inverse relationship type for bidirectional relationships."""
        return RELATIONSHIP_TYPES.get(
            self.relationship_type.lower(),
            self.relationship_type  # Return same type if not found
        )


def parse_relationship_line(line: str) -> Optional[tuple[str, Optional[str], str, str]]:
    """Parse a single relationship line.

    Args:
        line: A line from the Connections section

    Returns:
        Tuple of (target_name, target_file, relationship_type, description) or None

    Examples:
        >>> parse_relationship_line("- [Grimbold](grimbold.md) | ally | Old friend")
        ('Grimbold', 'grimbold.md', 'ally', 'Old friend')
        >>> parse_relationship_line("- The Shadow Guild | enemy | Hunted")
        ('The Shadow Guild', None, 'enemy', 'Hunted')
    """
    line = line.strip()

    # Must start with "- "
    if not line.startswith("- "):
        return None

    # Remove the leading "- "
    line = line[2:].strip()

    # Split by pipe
    parts = [p.strip() for p in line.split("|")]

    if len(parts) < 2:
        return None  # Need at least name and type

    name_part = parts[0]
    rel_type = parts[1].lower()
    description = parts[2] if len(parts) > 2 else ""

    # Parse the name part - could be [Name](file.md) or just Name
    # Pattern for markdown link: [Text](url)
    link_match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", name_part)

    if link_match:
        target_name = link_match.group(1)
        target_file = link_match.group(2)
    else:
        target_name = name_part
        target_file = None

    # Validate relationship type
    if rel_type not in RELATIONSHIP_TYPES:
        warnings.warn(
            f"Unknown relationship type '{rel_type}' for '{target_name}'. "
            f"Valid types: {', '.join(RELATIONSHIP_TYPES.keys())}"
        )

    return (target_name, target_file, rel_type, description)


def parse_connections_section(content: str) -> list[tuple[str, Optional[str], str, str]]:
    """Parse the Connections section from NPC file content.

    Args:
        content: Full markdown content of an NPC file

    Returns:
        List of tuples (target_name, target_file, relationship_type, description)
    """
    relationships = []

    # Find the Connections section
    connections_match = re.search(
        r"## Connections\s*\n(.*?)(?=\n## |\n---|\Z)",
        content,
        re.DOTALL
    )

    if not connections_match:
        return relationships

    connections_text = connections_match.group(1)

    # Parse each line
    for line in connections_text.split("\n"):
        line = line.strip()
        if line.startswith("- ") and "|" in line:
            parsed = parse_relationship_line(line)
            if parsed:
                relationships.append(parsed)

    return relationships


def extract_npc_name_from_file(content: str) -> Optional[str]:
    """Extract the NPC name from file content.

    Args:
        content: Full markdown content of an NPC file

    Returns:
        NPC name or None
    """
    # Look for the main heading
    match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def parse_connections_from_file(
    file_path: Path,
    source_name: Optional[str] = None,
    source_file: Optional[str] = None,
) -> list[Relationship]:
    """Parse all relationships from an NPC file.

    Args:
        file_path: Path to the NPC markdown file
        source_name: Name of the source NPC (auto-detected if not provided)
        source_file: Filename of source NPC (auto-detected if not provided)

    Returns:
        List of Relationship objects
    """
    if not file_path.exists():
        return []

    content = file_path.read_text(encoding="utf-8")

    # Get source info
    if source_name is None:
        source_name = extract_npc_name_from_file(content) or file_path.stem
    if source_file is None:
        source_file = file_path.name

    # Parse connections
    raw_relationships = parse_connections_section(content)

    # Build Relationship objects
    relationships = []
    for target_name, target_file, rel_type, description in raw_relationships:
        relationships.append(Relationship(
            source_name=source_name,
            source_file=source_file,
            target_name=target_name,
            target_file=target_file,
            relationship_type=rel_type,
            description=description,
        ))

    return relationships


def format_relationship_line(
    target_name: str,
    target_file: Optional[str],
    relationship_type: str,
    description: str = "",
) -> str:
    """Format a relationship as a markdown line.

    Args:
        target_name: Name of the target NPC
        target_file: Filename of target NPC (optional)
        relationship_type: Type of relationship
        description: Description of the relationship

    Returns:
        Formatted markdown line
    """
    if target_file:
        name_part = f"[{target_name}]({target_file})"
    else:
        name_part = target_name

    if description:
        return f"- {name_part} | {relationship_type} | {description}"
    else:
        return f"- {name_part} | {relationship_type}"


def add_relationship_to_content(
    content: str,
    target_name: str,
    target_file: Optional[str],
    relationship_type: str,
    description: str = "",
) -> str:
    """Add a relationship to NPC file content.

    Args:
        content: Existing NPC file content
        target_name: Name of the target NPC
        target_file: Filename of target NPC (optional)
        relationship_type: Type of relationship
        description: Description of the relationship

    Returns:
        Updated content with the new relationship
    """
    new_line = format_relationship_line(
        target_name, target_file, relationship_type, description
    )

    # Find the Connections section
    connections_match = re.search(
        r"(## Connections\s*\n)(.*?)(\n## |\n---|\Z)",
        content,
        re.DOTALL
    )

    if not connections_match:
        # No Connections section found - shouldn't happen with proper NPC files
        return content

    header = connections_match.group(1)
    section_content = connections_match.group(2)
    after = connections_match.group(3)

    # Check if this relationship already exists
    if target_name.lower() in section_content.lower():
        # Already exists, don't add duplicate
        return content

    # Remove placeholder text if present
    section_content = re.sub(
        r"\*List relationships.*?\*\s*\n?",
        "",
        section_content
    )

    # Add the new relationship
    section_content = section_content.rstrip() + "\n" + new_line + "\n"

    # Ensure proper spacing
    if not section_content.startswith("\n"):
        section_content = "\n" + section_content

    # Reconstruct the content
    start = content[:connections_match.start()]
    new_section = header + section_content
    end = after + content[connections_match.end():]

    return start + new_section + end
