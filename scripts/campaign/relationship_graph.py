#!/usr/bin/env python3
"""
Relationship Graph Generator - Generate Mermaid diagram of NPC relationships.

Scans all NPC files for relationships and generates a visual graph
showing how NPCs are connected.

Usage:
    python scripts/campaign/relationship_graph.py
    python scripts/campaign/relationship_graph.py --output relationships.md
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import bold, heading, horizontal_rule, iso_date, slugify
from lib.relationship_parser import Relationship, parse_connections_from_file


@dataclass
class NPCNode:
    """Represents an NPC in the relationship graph."""

    name: str
    slug: str
    file_path: Optional[str] = None
    relationships: list[Relationship] = field(default_factory=list)


def collect_all_relationships(npcs_dir: Path) -> tuple[dict[str, NPCNode], list[Relationship]]:
    """Collect all relationships from NPC files.

    Args:
        npcs_dir: Path to NPCs directory

    Returns:
        Tuple of (nodes dict, relationships list)
    """
    nodes: dict[str, NPCNode] = {}
    all_relationships: list[Relationship] = []

    if not npcs_dir.exists():
        return nodes, all_relationships

    for npc_file in sorted(npcs_dir.glob("*.md")):
        if npc_file.name == "index.md":
            continue

        # Parse relationships from this file
        relationships = parse_connections_from_file(npc_file)

        if not relationships:
            continue

        # Get source NPC info
        source_name = relationships[0].source_name if relationships else npc_file.stem
        source_slug = slugify(source_name)

        # Create or update source node
        if source_slug not in nodes:
            nodes[source_slug] = NPCNode(
                name=source_name,
                slug=source_slug,
                file_path=f"npcs/{npc_file.name}",
            )

        # Add relationships
        for rel in relationships:
            nodes[source_slug].relationships.append(rel)
            all_relationships.append(rel)

            # Create target node if it doesn't exist
            target_slug = slugify(rel.target_name)
            if target_slug not in nodes:
                target_file = rel.target_file
                if target_file and not target_file.startswith("npcs/"):
                    target_file = f"npcs/{target_file}"
                nodes[target_slug] = NPCNode(
                    name=rel.target_name,
                    slug=target_slug,
                    file_path=target_file,
                )

    return nodes, all_relationships


def generate_mermaid(nodes: dict[str, NPCNode], relationships: list[Relationship]) -> str:
    """Generate Mermaid flowchart from nodes and relationships.

    Args:
        nodes: Dict of slug to NPCNode
        relationships: List of all relationships

    Returns:
        Mermaid diagram as string
    """
    if not nodes:
        return ""

    lines = ["```mermaid", "flowchart LR"]

    # Add node definitions
    for slug, node in sorted(nodes.items()):
        # Escape special characters in node labels
        safe_name = node.name.replace('"', '\\"')
        lines.append(f'    {slug}["{safe_name}"]')

    lines.append("")

    # Add edges
    seen_edges = set()
    for rel in relationships:
        source_slug = slugify(rel.source_name)
        target_slug = slugify(rel.target_name)

        # Skip self-references
        if source_slug == target_slug:
            continue

        # Create edge key to avoid duplicates
        edge_key = (source_slug, target_slug, rel.relationship_type)
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        lines.append(f"    {source_slug} -->|{rel.relationship_type}| {target_slug}")

    lines.append("```")

    return "\n".join(lines)


def generate_legend() -> str:
    """Generate relationship type legend."""
    return """## Relationship Types

| Type | Description |
|------|-------------|
| ally | Friendly, cooperative |
| enemy | Hostile, adversarial |
| family | Blood or marriage relation |
| employer | Works for this person |
| employee | This person works for them |
| rival | Competitive relationship |
| neutral | Knows but no strong feelings |
| romantic | Love interest |
| mentor | Teacher |
| student | Learner |"""


def generate_relationships_file(
    campaign_dir: Path,
    output_path: Path,
) -> dict:
    """Generate the complete relationships.md file.

    Args:
        campaign_dir: Path to campaign directory
        output_path: Path to output file

    Returns:
        Statistics about the generated graph
    """
    npcs_dir = campaign_dir / "npcs"
    nodes, relationships = collect_all_relationships(npcs_dir)

    # Build content
    lines = [
        "# NPC Relationships",
        "",
        f"{bold('Generated')}: {iso_date()}  ",
        f"{bold('NPCs')}: {len(nodes)}  ",
        f"{bold('Connections')}: {len(relationships)}",
        "",
        horizontal_rule(),
        "",
    ]

    if not relationships:
        lines.append("*No relationships found. Add relationships to NPC files using:*")
        lines.append("")
        lines.append("```bash")
        lines.append('python scripts/campaign/campaign_manager.py add-relationship "NPC A" "NPC B" --type ally')
        lines.append("```")
        lines.append("")
        lines.append("*Or edit NPC files directly in the `## Connections` section:*")
        lines.append("")
        lines.append("```markdown")
        lines.append("## Connections")
        lines.append("")
        lines.append("- [Other NPC](other-npc.md) | ally | Description of relationship")
        lines.append("```")
    else:
        # Add Mermaid diagram
        mermaid = generate_mermaid(nodes, relationships)
        lines.append(mermaid)
        lines.append("")

        # Add relationship list by NPC
        lines.append("## Relationships by NPC")
        lines.append("")

        for slug, node in sorted(nodes.items()):
            if not node.relationships:
                continue

            if node.file_path:
                lines.append(f"### [{node.name}]({node.file_path})")
            else:
                lines.append(f"### {node.name}")
            lines.append("")

            for rel in node.relationships:
                if rel.target_file:
                    target_path = rel.target_file if rel.target_file.startswith("npcs/") else f"npcs/{rel.target_file}"
                    target_link = f"[{rel.target_name}]({target_path})"
                else:
                    target_link = rel.target_name

                desc = f" - {rel.description}" if rel.description else ""
                lines.append(f"- {target_link} ({rel.relationship_type}){desc}")

            lines.append("")

    lines.append(horizontal_rule())
    lines.append("")
    lines.append(generate_legend())
    lines.append("")
    lines.append(horizontal_rule())
    lines.append("")
    lines.append(f"*Graph generated on {iso_date()}*")

    # Write to file
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "npcs": len(nodes),
        "relationships": len(relationships),
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
        description="Generate a Mermaid diagram of NPC relationships.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/relationship_graph.py
    python scripts/campaign/relationship_graph.py --output custom-graph.md

The graph includes:
    - All NPCs with defined relationships
    - Relationship types as edge labels
    - Links to NPC files
        """,
    )

    parser.add_argument(
        "--output", "-o",
        default="relationships.md",
        help="Output filename (default: relationships.md)",
    )

    args = parser.parse_args()

    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"

    if not campaign_dir.exists():
        print("Error: Campaign directory not found. Run init_campaign.py first.")
        sys.exit(1)

    output_path = campaign_dir / args.output

    print("Generating NPC relationship graph...")
    stats = generate_relationships_file(campaign_dir, output_path)

    print()
    print(f"Graph: {output_path.relative_to(repo_root)}")
    print()
    print(f"NPCs with relationships: {stats['npcs']}")
    print(f"Total relationships: {stats['relationships']}")


if __name__ == "__main__":
    main()
