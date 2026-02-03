"""Tests for relationship_graph.py"""

import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from campaign.relationship_graph import (
    NPCNode,
    collect_all_relationships,
    generate_mermaid,
    generate_relationships_file,
)
from lib.relationship_parser import Relationship


class TestCollectAllRelationships:
    """Tests for collecting relationships from NPC files."""

    def test_collect_from_single_npc(self, tmp_path):
        """Test collecting relationships from a single NPC file."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        npc_content = """# Elara the Wise

## Connections

- [Grimbold](grimbold.md) | ally | Old friend

## Secrets
"""
        (npcs_dir / "elara-the-wise.md").write_text(npc_content)

        nodes, relationships = collect_all_relationships(npcs_dir)

        assert len(nodes) == 2  # Elara and Grimbold (from relationship)
        assert len(relationships) == 1
        assert "elara-the-wise" in nodes  # slugify uses hyphens
        assert relationships[0].source_name == "Elara the Wise"
        assert relationships[0].target_name == "Grimbold"

    def test_collect_from_multiple_npcs(self, tmp_path):
        """Test collecting relationships from multiple NPC files."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        # NPC 1
        (npcs_dir / "elara.md").write_text("""# Elara

## Connections

- [Grimbold](grimbold.md) | ally | Friends

## Secrets
""")

        # NPC 2
        (npcs_dir / "grimbold.md").write_text("""# Grimbold

## Connections

- [Elara](elara.md) | ally | Friends
- [Mayor](mayor.md) | employer | Works for

## Secrets
""")

        nodes, relationships = collect_all_relationships(npcs_dir)

        assert len(nodes) >= 3  # At least Elara, Grimbold, Mayor
        assert len(relationships) == 3  # 1 from Elara, 2 from Grimbold

    def test_skip_index_file(self, tmp_path):
        """Test that index.md is skipped."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        # Index file should be ignored
        (npcs_dir / "index.md").write_text("""# NPCs

- [Test](test.md) | ally | Should be ignored
""")

        # Regular NPC file
        (npcs_dir / "test.md").write_text("""# Test NPC

## Connections

- [Friend](friend.md) | ally | Real relationship

## Secrets
""")

        nodes, relationships = collect_all_relationships(npcs_dir)

        # Should only have relationships from test.md, not index.md
        assert len(relationships) == 1
        assert relationships[0].source_name == "Test NPC"

    def test_empty_directory(self, tmp_path):
        """Test collecting from an empty directory."""
        npcs_dir = tmp_path / "npcs"
        npcs_dir.mkdir()

        nodes, relationships = collect_all_relationships(npcs_dir)

        assert len(nodes) == 0
        assert len(relationships) == 0

    def test_nonexistent_directory(self, tmp_path):
        """Test collecting from a non-existent directory."""
        npcs_dir = tmp_path / "npcs"  # Not created

        nodes, relationships = collect_all_relationships(npcs_dir)

        assert len(nodes) == 0
        assert len(relationships) == 0


class TestGenerateMermaid:
    """Tests for Mermaid diagram generation."""

    def test_generate_simple_graph(self):
        """Test generating a simple graph."""
        nodes = {
            "elara": NPCNode(name="Elara", slug="elara", file_path="npcs/elara.md"),
            "grimbold": NPCNode(name="Grimbold", slug="grimbold", file_path="npcs/grimbold.md"),
        }

        relationships = [
            Relationship(
                source_name="Elara", source_file="elara.md",
                target_name="Grimbold", target_file="grimbold.md",
                relationship_type="ally", description="Friends"
            )
        ]

        mermaid = generate_mermaid(nodes, relationships)

        assert "```mermaid" in mermaid
        assert "flowchart LR" in mermaid
        assert 'elara["Elara"]' in mermaid
        assert 'grimbold["Grimbold"]' in mermaid
        assert "elara -->|ally| grimbold" in mermaid
        assert "```" in mermaid

    def test_generate_empty_graph(self):
        """Test generating with no nodes."""
        mermaid = generate_mermaid({}, [])
        assert mermaid == ""

    def test_skip_self_references(self):
        """Test that self-references are skipped."""
        nodes = {
            "elara": NPCNode(name="Elara", slug="elara"),
        }

        relationships = [
            Relationship(
                source_name="Elara", source_file=None,
                target_name="Elara", target_file=None,  # Self-reference
                relationship_type="neutral", description=""
            )
        ]

        mermaid = generate_mermaid(nodes, relationships)

        # Should have nodes but no edges (self-reference skipped)
        assert "elara -->|" not in mermaid

    def test_escape_special_characters(self):
        """Test that special characters in names are escaped."""
        nodes = {
            "test": NPCNode(name='Test "Quote" NPC', slug="test"),
        }

        mermaid = generate_mermaid(nodes, [])

        # Should escape the quotes
        assert 'Test \\"Quote\\" NPC' in mermaid


class TestGenerateRelationshipsFile:
    """Tests for full relationship file generation."""

    def test_generate_complete_file(self, tmp_path):
        """Test generating a complete relationships file."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()
        npcs_dir = campaign_dir / "npcs"
        npcs_dir.mkdir()

        # Create NPC with relationships
        (npcs_dir / "elara.md").write_text("""# Elara

## Connections

- [Grimbold](grimbold.md) | ally | Friends

## Secrets
""")

        output_path = campaign_dir / "relationships.md"
        stats = generate_relationships_file(campaign_dir, output_path)

        assert output_path.exists()
        assert stats["npcs"] >= 1
        assert stats["relationships"] == 1

        content = output_path.read_text()
        assert "# NPC Relationships" in content
        assert "```mermaid" in content
        assert "ally" in content

    def test_generate_empty_file(self, tmp_path):
        """Test generating when no relationships exist."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()
        npcs_dir = campaign_dir / "npcs"
        npcs_dir.mkdir()

        # NPC with no relationships
        (npcs_dir / "lonely.md").write_text("""# Lonely NPC

## Connections

*No relationships*

## Secrets
""")

        output_path = campaign_dir / "relationships.md"
        stats = generate_relationships_file(campaign_dir, output_path)

        assert output_path.exists()
        assert stats["relationships"] == 0

        content = output_path.read_text()
        assert "No relationships found" in content

    def test_relationships_by_npc_section(self, tmp_path):
        """Test that the 'Relationships by NPC' section is generated."""
        campaign_dir = tmp_path / "campaign"
        campaign_dir.mkdir()
        npcs_dir = campaign_dir / "npcs"
        npcs_dir.mkdir()

        (npcs_dir / "elara.md").write_text("""# Elara

## Connections

- [Grimbold](grimbold.md) | ally | Friend
- [Enemy](enemy.md) | enemy | Foe

## Secrets
""")

        output_path = campaign_dir / "relationships.md"
        generate_relationships_file(campaign_dir, output_path)

        content = output_path.read_text()
        assert "## Relationships by NPC" in content
        assert "### [Elara]" in content


class TestNPCNode:
    """Tests for the NPCNode dataclass."""

    def test_node_with_relationships(self):
        """Test creating a node with relationships."""
        rel = Relationship(
            source_name="Test", source_file="test.md",
            target_name="Target", target_file="target.md",
            relationship_type="ally", description="Friends"
        )

        node = NPCNode(
            name="Test",
            slug="test",
            file_path="npcs/test.md",
            relationships=[rel]
        )

        assert node.name == "Test"
        assert node.slug == "test"
        assert len(node.relationships) == 1

    def test_node_default_relationships(self):
        """Test that relationships default to empty list."""
        node = NPCNode(name="Test", slug="test")
        assert node.relationships == []
